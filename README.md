# CentrAlign AI Worker — Gemini-powered MVP

A narrow autonomous AI worker that processes an invoice using a simulated finance system. The model chooses tools, observes results, and must verify the final state before claiming success.

## Setup (macOS)

1. Install Python 3.10+ and create/activate a virtual environment.
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Get a Gemini API key from [Google AI Studio](https://aistudio.google.com/apikey). The Gemini API offers a free tier for eligible models, subject to rate limits.
4. Create your local environment file and add the key:
   ```bash
   cp .env.example .env
   ```
   Edit `.env` and replace `your_api_key_here` with your key. Never commit `.env`.
5. Run the worker:
   ```bash
   python main.py
   ```

The CLI stays running so you can enter multiple tasks in one session. Type `exit` to quit. Press Enter to run the demo task.

## Demo task

> Find the latest invoice from ABC Ltd and add it to the finance system.

The worker can call `search_invoices`, `get_invoice`, `update_finance_system`, `verify_invoice`, and `get_finance_record`. The finance system is simulated with local JSON data; no real finance system is changed.

## Design choices

- **Narrow scope:** invoice processing keeps the prototype focused on the task-worker brief.
- **Tool-driven execution:** the model chooses the next action from a small allowlist of typed tools.
- **Verification gate:** success is reported only after `verify_invoice` returns `verified=true`.
- **Bounded execution:** at most 10 tool calls per task to avoid runaway loops.
- **Observable behavior:** each tool call and result is printed for the demo.

## Limitations and next steps

- Gemini free-tier quotas and model availability can vary by account and region.
- The finance system is local simulation, not a production integration.
- No persistent long-term memory, authentication, or approval UI yet.
- Next: add unit tests, a browser/UI, explicit approval for consequential actions, and robust retry/backoff for rate limits.

## Iteration 2B: Tool Failure + Recovery

The prototype can simulate a temporary finance-system failure so the agent's recovery behavior can be demonstrated.

For the demo, add this to `.env`:

```env
SIMULATE_TOOL_FAILURE_ONCE=true
```

On the first `update_finance_system` call, the tool returns a temporary failure. The model receives the failure and should retry the update. The workflow should then continue to `verify_invoice` and only report success after verification.

To return to the normal workflow, set:

```env
SIMULATE_TOOL_FAILURE_ONCE=false
```


## Iteration 3: Generalized invoice tasks

The same agent can handle different natural-language tasks without separate hard-coded workflows, including:

1. Find the latest invoice from a company and add it to the finance system.
2. Add a specific invoice by invoice ID.
3. Check whether a specific invoice has been processed.
4. Find all invoices for a company and summarize them.

For write tasks, the worker still requires `verify_invoice` before claiming success. For read-only tasks, a successful tool result is sufficient.

## Interactive loop

The program continues accepting tasks until the user enters:

```text
exit
```

Each new task starts a fresh agent run while the CLI process remains active.
