# CentrAlign AI Worker — Gemini-Powered MVP

A narrow autonomous AI worker that processes invoice-related tasks using a simulated finance system. The worker accepts natural-language instructions, selects tools, observes their results, handles failures, and verifies the final state before claiming a write operation succeeded.

**Live Demo:** [Insert your deployed Streamlit URL]

**Source Code:** https://github.com/raoarpittt/centralign-ai-worker

## Features

- Natural-language task input through a Streamlit web interface and CLI.
- LLM-driven tool selection using Gemini.
- Invoice search and retrieval.
- Simulated finance-system updates.
- Execution history and tool-result visibility.
- Bounded execution and retry handling.
- Verification of write operations before reporting success.
- Clarification handling for ambiguous requests, subject to the current interface limitations.

## Architecture

The application consists of the following components:

- `app.py`: Streamlit interface for submitting tasks and viewing execution results.
- `main.py`: CLI entry point for running tasks interactively.
- `agent/worker.py`: Agent execution loop, Gemini integration, tool selection, and execution control.
- `agent/state.py`: Tracks execution steps, discovered facts, completion status, and the final response.
- `tools/`: Contains the available invoice and finance-system tools.
- `data/`: Contains local JSON records used by the simulated environment.

The worker sends the task to Gemini, executes selected tools, observes their results, and continues until the task is completed, blocked, or the execution limit is reached. Write tasks require a successful verification result before being reported as complete.

## Setup

### Requirements

- Python 3.10 or later, compatible with the project's dependencies.
- A Gemini API key.
- Dependencies listed in `requirements.txt`.

### Local installation

1. Clone the repository:

   `git clone https://github.com/raoarpittt/centralign-ai-worker.git`

2. Enter the project directory:

   `cd centralign-ai-worker`

3. Create and activate a virtual environment:

   `python3 -m venv venv`

   `source venv/bin/activate`

4. Install dependencies:

   `pip install -r requirements.txt`

5. Create the local environment file:

   `cp .env.example .env`

6. Add your Gemini API key to `.env`. Never commit this file or expose the key.

### Run the web interface

`streamlit run app.py`

### Run the CLI

`python main.py`

## Demo Task

Find the latest invoice from ABC Ltd and add it to the finance system.

The available tools include `search_invoices`, `get_invoice`, `update_finance_system`, `verify_invoice`, and `get_finance_record`.

The finance system is simulated using local JSON data. No real external finance system is modified.

## Design Decisions

- **Narrow scope:** Invoice processing keeps the prototype focused on a concrete business workflow.
- **Tool-driven execution:** Gemini selects from a predefined set of available tools.
- **Verification gate:** Write-task success depends on `verify_invoice` returning `verified=true`.
- **Bounded execution:** Each task has a maximum step limit to prevent unbounded execution.
- **Observability:** Tool calls and results are exposed to help users understand the execution process.
- **Simulated environment:** Local data enables demonstration without production credentials or unauthorized access.

## Assumptions

- Invoice records are available in the local simulated dataset.
- The model can choose among the tools exposed by the application.
- The prototype is intended to demonstrate a limited invoice-processing workflow, not arbitrary computer use.
- Finance-system updates affect the simulated environment only.

## Known Limitations

- The application supports a limited invoice-processing workflow.
- The finance system is simulated rather than connected to a production service.
- Model availability, latency, and API quotas can affect execution.
- Execution is bounded by a configured step limit.
- Browser-based clarification and human-approval handling may need further development.
- Automated test coverage and production-grade security controls remain future work.

## Future Improvements

1. Add automated tests for successful tasks, tool failures, retries, and failed verification.
2. Implement browser-native clarification and human-approval workflows.
3. Improve structured error handling and retry policies.
4. Add persistent audit logs and execution-history storage.
5. Integrate external business systems through authenticated APIs.
6. Expand evaluation across different task types and unexpected tool results.

## Technology Stack

- Python
- Google Gemini API and Google Gen AI SDK
- Streamlit
- JSON-based simulated invoice and finance records
- Additional dependencies listed in `requirements.txt`

## Demo

- **Live application:** [Insert your deployed Streamlit URL]
- **Demo video:** [Insert your recording link, if available]
