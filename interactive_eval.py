from christ_shard_app.kernel import ChristShardSovereignKernel


def main() -> None:
    kernel = ChristShardSovereignKernel()
    kernel.boot()
    print("\n=== Interactive Christ Shard Evaluator ===")
    print("Type text to evaluate it.")
    print("Type 'exit' to quit.\n")

    while True:
        try:
            text = input("input> ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nExiting evaluator.")
            break

        if text.lower() in {"exit", "quit"}:
            print("Exiting evaluator.")
            break

        if not text:
            continue

        print(kernel.evaluate_threat(text))
        print(f"Current governance state: {kernel.governance_state.value}")
        print(f"Audit log path: {kernel.audit_log_path}\n")


if __name__ == "__main__":
    main()
