import json
import os
from dotenv import load_dotenv
from google import genai
from google.genai import types

from .state import AgentState
from tools.registry import TOOLS

load_dotenv()

SYSTEM_INSTRUCTIONS = """
You are an autonomous invoice-processing worker operating in a simulated company environment.
Complete the user's task by choosing and using the available tools. Do not just describe actions; call tools to perform them.

Available tools:
- search_invoices(company): find invoices for a company, newest first.
- get_invoice(invoice_id): retrieve invoice details.
- update_finance_system(invoice_id, company, amount, due_date): store the invoice in the finance system.
- verify_invoice(invoice_id, expected_amount, expected_due_date): check that the stored record matches the expected values.
- get_finance_record(invoice_id): check whether an invoice has been processed in the finance system.

Rules:
1. Work one step at a time and inspect tool results before choosing the next action.
2. Use the invoice date to identify the latest invoice. Do not assume the first result without inspecting the search results.
3. Use actual values returned by tools; never invent invoice details.
4. Do not say the task succeeded unless verify_invoice returns verified=true.
5. If the task is ambiguous and you cannot safely choose, ask the user a concise clarification question.
6. If a tool fails with a temporary or retryable error, retry the same tool with the same arguments once before trying a different approach. Do not retry indefinitely.
7. If an action fails, do not claim success; continue only after a successful action or explain why the task could not be completed.
8. For read-only tasks such as checking status or listing invoices, a successful tool result is sufficient; do not force an update/verification workflow that the user did not request.
9. When done, give a concise summary of what was actually completed.
""".strip()

TOOL_SCHEMAS = [
    {
        "type": "function",
        "name": "search_invoices",
        "description": "Find invoices for a company. Results are sorted newest first by invoice date.",
        "parameters": {
            "type": "object",
            "properties": {"company": {"type": "string", "description": "Company or vendor name"}},
            "required": ["company"],
            "additionalProperties": False,
        },
        "strict": True,
    },
    {
        "type": "function",
        "name": "get_invoice",
        "description": "Retrieve full details for a specific invoice ID.",
        "parameters": {
            "type": "object",
            "properties": {"invoice_id": {"type": "string"}},
            "required": ["invoice_id"],
            "additionalProperties": False,
        },
        "strict": True,
    },
    {
        "type": "function",
        "name": "update_finance_system",
        "description": "Insert or update an invoice in the simulated finance system.",
        "parameters": {
            "type": "object",
            "properties": {
                "invoice_id": {"type": "string"},
                "company": {"type": "string"},
                "amount": {"type": "number"},
                "due_date": {"type": "string"},
            },
            "required": ["invoice_id", "company", "amount", "due_date"],
            "additionalProperties": False,
        },
        "strict": True,
    },
    {
        "type": "function",
        "name": "get_finance_record",
        "description": "Check whether a specific invoice has been processed in the simulated finance system and return its current status.",
        "parameters": {
            "type": "object",
            "properties": {
                "invoice_id": {"type": "string"},
            },
            "required": ["invoice_id"],
            "additionalProperties": False,
        },
        "strict": True,
    },
    {
        "type": "function",
        "name": "verify_invoice",
        "description": "Verify that the invoice exists in the finance system and its amount and due date match.",
        "parameters": {
            "type": "object",
            "properties": {
                "invoice_id": {"type": "string"},
                "expected_amount": {"type": "number"},
                "expected_due_date": {"type": "string"},
            },
            "required": ["invoice_id", "expected_amount", "expected_due_date"],
            "additionalProperties": False,
        },
        "strict": True,
    },
]


def _send_with_retry(chat, message, max_retries: int = 3):
    """Send a Gemini request and retry temporary 429/503 failures."""
    import time

    for attempt in range(max_retries + 1):
        try:
            return chat.send_message(message)
        except Exception as exc:
            error_text = str(exc)
            is_transient = "429" in error_text or "503" in error_text
            if not is_transient or attempt >= max_retries:
                raise

            delay = 2 ** attempt
            print(
                f"\nTemporary Gemini error ({'429 rate limit' if '429' in error_text else '503 unavailable'}). "
                f"Retrying in {delay}s... ({attempt + 1}/{max_retries})"
            )
            time.sleep(delay)


def run_worker(task: str, max_steps: int = 10) -> AgentState:
    """Run an LLM-driven tool loop using Google's Gemini API free tier."""
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise RuntimeError("GEMINI_API_KEY is missing. Copy .env.example to .env and add your Google AI Studio API key.")

    client = genai.Client(api_key=api_key)
    model = os.getenv("GEMINI_MODEL", "gemini-3.8-flash").strip()
    print(f"MODEL: {model}")
    declarations = [
        types.FunctionDeclaration(
            name=tool["name"],
            description=tool["description"],
            parameters_json_schema=tool["parameters"],
        )
        for tool in TOOL_SCHEMAS
    ]
    chat = client.chats.create(
        model=model,
        config=types.GenerateContentConfig(
            system_instruction=SYSTEM_INSTRUCTIONS,
            tools=[types.Tool(function_declarations=declarations)],
            temperature=0.1,
        ),
    )
    state = AgentState(task=task)
    tool_steps = 0

    print(f"TASK: {task}\n")
    response = _send_with_retry(chat, task)

    while tool_steps < max_steps:
        function_calls = []
        if response.candidates:
            for part in response.candidates[0].content.parts or []:
                if part.function_call:
                    function_calls.append(part.function_call)

        if not function_calls:
            message = (response.text or "The model returned no response.").strip()
            verified = any(
                step["action"].get("tool") == "verify_invoice"
                and step["result"].get("verified") is True
                for step in state.steps
            )
            has_update = any(
                step["action"].get("tool") == "update_finance_system"
                for step in state.steps
            )
            successful_tool = any(
                step["result"].get("success") is True
                for step in state.steps
            )
            if verified or (successful_tool and not has_update):
                state.completed = True
                state.final_message = message
                print(f"\nFINAL: {message}")
                return state

            lower_message = message.lower()
            is_clarification = (
                "?" in message
                or any(
                    word in lower_message
                    for word in (
                        "which invoice",
                        "which company",
                        "which vendor",
                        "could you clarify",
                        "please clarify",
                        "what company",
                        "what vendor",
                        "need more information",
                    )
                )
            )
            if is_clarification:
                print(f"\nNEEDS CLARIFICATION: {message}")
                clarification = input("\nYour answer: ").strip()
                if not clarification:
                    state.final_message = message
                    return state

                # Continue the existing Gemini chat with the user's answer.
                # This preserves the original task and all prior tool/context state.
                response = _send_with_retry(
                    chat,
                    f"User clarification: {clarification}",
                )
                continue

            state.final_message = "The model stopped before the requested outcome could be verified. " + message
            print(f"\nNOT VERIFIED: {state.final_message}")
            return state

        for call in function_calls:
            if tool_steps >= max_steps:
                break
            tool_steps += 1
            tool_name = call.name
            arguments = dict(call.args or {})
            try:
                if tool_name not in TOOLS:
                    result = {"success": False, "error": f"Unknown tool: {tool_name}"}
                else:
                    result = TOOLS[tool_name](**arguments)
            except Exception as exc:
                result = {"success": False, "error": str(exc)}

            action = {"type": "tool_call", "tool": tool_name, "arguments": arguments}
            state.add_step(action, result)
            print(f"{tool_steps}. {tool_name}({json.dumps(arguments)})")
            print(f"   -> {json.dumps(result, ensure_ascii=False)}")

            if result.get("success") and tool_name == "get_invoice":
                state.facts.update(result.get("invoice", {}))
            if tool_name == "verify_invoice" and result.get("verified") is True:
                state.completed = True

            response = _send_with_retry(
                chat,
                types.Part.from_function_response(name=tool_name, response=result),
            )

    state.final_message = f"Stopped after reaching the {max_steps}-tool-call limit. Task completion was not assumed."
    print(f"\nSTOPPED: {state.final_message}")
    return state
