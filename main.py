from agent.worker import run_worker


def main():
    print("CentrAlign AI Worker")
    print("Enter a task at any time. Type 'exit' to quit.\n")

    while True:
        task = input("Task: ").strip()

        if task.lower() == "exit":
            print("\nExiting CentrAlign AI Worker.")
            break

        if not task:
            task = "Find the latest invoice from ABC Ltd and add it to the finance system."
            print(f"Using demo task: {task}")

        try:
            state = run_worker(task, max_steps=10)
        except Exception as exc:
            print(f"\nERROR: {exc}")
            continue

        print("\n--- RUN SUMMARY ---")
        print(f"Tool calls: {len(state.steps)}")
        print(f"Verified completion: {state.completed}")
        print(f"Final message: {state.final_message}")
        print("\nEnter another task, or type 'exit' to quit.\n")


if __name__ == "__main__":
    main()
