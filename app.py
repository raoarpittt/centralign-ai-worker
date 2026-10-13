
import streamlit as st
from agent.worker import run_worker

st.set_page_config(
    page_title="CentrAlign AI Worker",
    page_icon="🤖",
    layout="wide",
)

st.title("CentrAlign AI Worker")
st.caption("Autonomous invoice processing · Gemini-powered prototype")

if "history" not in st.session_state:
    st.session_state.history = []

with st.sidebar:
    st.subheader("About this worker")
    st.write("Processes invoice tasks using an LLM and simulated finance tools.")
    st.write("**Capabilities**")
    st.write("- Natural-language task understanding")
    st.write("- Tool selection and execution")
    st.write("- Retry and recovery logic")
    st.write("- Outcome verification")
    st.divider()
    if st.button("Clear history"):
        st.session_state.history = []
        st.rerun()

st.subheader("Enter a task")

task = st.text_area(
    "What should the agent do?",
    placeholder="Find the latest invoice from ABC Ltd and add it to the finance system.",
    height=100,
)

run_clicked = st.button("Run task", type="primary")

if run_clicked:
    if not task.strip():
        st.warning("Please enter a task first.")
    else:
        with st.spinner("Agent is working..."):
            try:
                state = run_worker(task.strip(), max_steps=10)
                st.session_state.history.insert(0, {
                    "task": task.strip(),
                    "steps": state.steps,
                    "completed": state.completed,
                    "final_message": state.final_message or "No final message returned.",
                })
                st.session_state.last_error = None
            except Exception as exc:
                st.session_state.last_error = str(exc)

if st.session_state.get("last_error"):
    st.error(f"Agent error: {st.session_state.last_error}")

if st.session_state.history:
    st.divider()
    st.subheader("Execution results")

    for index, run in enumerate(st.session_state.history):
        with st.expander(run["task"], expanded=(index == 0)):
            if run["completed"]:
                st.success("Task completed")
            else:
                st.warning("Task not verified as complete")

            st.markdown("**Final response**")
            st.write(run["final_message"])

            st.markdown(f"**Tool calls:** {len(run['steps'])}")

            for number, step in enumerate(run["steps"], start=1):
                action = step.get("action", {})
                result = step.get("result", {})

                with st.container(border=True):
                    st.markdown(
                        f"**{number}. {action.get('tool', 'Unknown tool')}**"
                    )
                    st.markdown("Arguments")
                    st.json(action.get("arguments", {}))
                    st.markdown("Result")
                    st.json(result)

            st.caption(
                "Completion is based on the worker's status. "
                "For write operations, confirm that invoice verification succeeded."
            )
else:
    st.info("Enter a task above to start your first run.")
