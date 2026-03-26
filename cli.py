from __future__ import annotations

import argparse
import json
from pathlib import Path

from christ_shard_app.kernel import (
    CORE_MANIFEST_PATH,
    EXPECTED_SHARD_FINGERPRINT,
    POLICY_PATH,
    ChristShard,
    ChristShardSovereignKernel,
)
from christ_shard_app.storage import read_json, write_json


STATE_DIR = Path("state")
AUDIT_LOG_PATH = STATE_DIR / "audit_log.json"
LAST_DECISION_PATH = STATE_DIR / "last_decision.json"
ANTIGEN_MEMORY_PATH = STATE_DIR / "antigen_memory.json"
HEALTH_REPORT_PATH = STATE_DIR / "health_report.json"


def build_health_summary() -> dict:
    shard = ChristShard()
    actual_fingerprint = shard.fingerprint()
    integrity_match = actual_fingerprint == EXPECTED_SHARD_FINGERPRINT
    policy = read_json(POLICY_PATH, default={})
    last_decision = read_json(LAST_DECISION_PATH, default={})

    state_files = {
        "audit_log_present": AUDIT_LOG_PATH.exists(),
        "last_decision_present": LAST_DECISION_PATH.exists(),
        "antigen_memory_present": ANTIGEN_MEMORY_PATH.exists(),
    }

    return {
        "manifest_path": str(CORE_MANIFEST_PATH),
        "policy_path": str(POLICY_PATH),
        "integrity_verified": integrity_match,
        "expected_fingerprint": EXPECTED_SHARD_FINGERPRINT,
        "actual_fingerprint": actual_fingerprint,
        "state_files": state_files,
        "active_policy": policy,
        "last_saved_decision": last_decision if last_decision else None,
    }


def cmd_eval(text: str) -> None:
    kernel = ChristShardSovereignKernel()
    kernel.boot()
    print(kernel.evaluate_threat(text))
    print(f"Current governance state: {kernel.governance_state.value}")
    print(f"Audit log path: {kernel.audit_log_path}")
    print(f"Last decision path: {kernel.last_decision_path}")
    print(f"Antigen memory path: {kernel.antigen_memory_path}")


def cmd_status() -> None:
    last_decision = read_json(LAST_DECISION_PATH, default={})
    if not last_decision:
        print("No saved decision found.")
        return

    print("=== Last Saved Decision ===")
    print(json.dumps(last_decision, indent=2, sort_keys=True))


def cmd_memory() -> None:
    memory = read_json(ANTIGEN_MEMORY_PATH, default=[])
    print("=== Antigen Memory ===")
    print(json.dumps(memory, indent=2, sort_keys=True))


def cmd_verify() -> None:
    shard = ChristShard()
    actual_fingerprint = shard.fingerprint()
    match = actual_fingerprint == EXPECTED_SHARD_FINGERPRINT

    print("=== Christ Shard Integrity Verification ===")
    print(f"Manifest path: {CORE_MANIFEST_PATH}")
    print(f"Expected fingerprint: {EXPECTED_SHARD_FINGERPRINT}")
    print(f"Actual fingerprint:   {actual_fingerprint}")
    print(f"Integrity match:      {match}")

    if match:
        print("Integrity status: VERIFIED")
    else:
        print("Integrity status: MISMATCH")


def cmd_policy() -> None:
    policy = read_json(POLICY_PATH, default={})
    print("=== Active Governance Policy ===")
    print(f"Policy path: {POLICY_PATH}")
    print(json.dumps(policy, indent=2, sort_keys=True))


def cmd_audit(limit: int) -> None:
    audit_log = read_json(AUDIT_LOG_PATH, default=[])
    if not isinstance(audit_log, list) or not audit_log:
        print("No audit history found.")
        return

    shown = audit_log[-limit:]
    print("=== Recent Audit History ===")
    print(f"Audit log path: {AUDIT_LOG_PATH}")
    print(f"Showing last {len(shown)} event(s)")
    print(json.dumps(shown, indent=2, sort_keys=True))


def cmd_reset(yes: bool) -> None:
    if not yes:
        print("Reset aborted. Re-run with: python3 cli.py reset --yes")
        return

    targets = [
        AUDIT_LOG_PATH,
        LAST_DECISION_PATH,
        ANTIGEN_MEMORY_PATH,
        HEALTH_REPORT_PATH,
    ]

    removed = []
    for path in targets:
        if path.exists():
            path.unlink()
            removed.append(str(path))

    print("=== Runtime State Reset ===")
    if removed:
        print("Removed:")
        for item in removed:
            print(f"- {item}")
    else:
        print("No runtime state files were present.")

    if STATE_DIR.exists():
        remaining = sorted(p.name for p in STATE_DIR.iterdir())
        if remaining:
            print("Remaining files in state/:")
            for name in remaining:
                print(f"- {name}")
        else:
            print("state/ is now empty.")


def cmd_health() -> None:
    summary = build_health_summary()

    print("=== Christ Shard Defense Health Summary ===")
    print(f"Manifest path: {summary['manifest_path']}")
    print(f"Policy path:   {summary['policy_path']}")
    print(f"Integrity verified: {summary['integrity_verified']}")
    print(f"Expected fingerprint: {summary['expected_fingerprint']}")
    print(f"Actual fingerprint:   {summary['actual_fingerprint']}")

    print("\nState files:")
    print(json.dumps(summary["state_files"], indent=2, sort_keys=True))

    print("\nActive policy:")
    print(json.dumps(summary["active_policy"], indent=2, sort_keys=True))

    if summary["last_saved_decision"]:
        print("\nLast saved decision:")
        print(json.dumps(summary["last_saved_decision"], indent=2, sort_keys=True))
    else:
        print("\nLast saved decision: none")


def cmd_report(path_str: str) -> None:
    path = Path(path_str)
    summary = build_health_summary()
    write_json(path, summary)
    print("=== Health Report Exported ===")
    print(f"Report path: {path}")
    print(json.dumps(summary, indent=2, sort_keys=True))


def _run_sequence(sequence: list[str]) -> None:
    kernel = ChristShardSovereignKernel()
    kernel.boot()

    print("=== Christ Shard Defense Simulation ===")
    print(f"Scenario length: {len(sequence)}")
    print(f"Policy path: {POLICY_PATH}")
    print()

    for idx, text in enumerate(sequence, start=1):
        print(f"[Step {idx}] Input: {text}")
        result = kernel.evaluate_threat(text)
        print(result)
        print(f"Governance state after step {idx}: {kernel.governance_state.value}")
        print()

    print("Simulation completed.")
    print(f"Final governance state: {kernel.governance_state.value}")
    print(f"Audit log path: {kernel.audit_log_path}")
    print(f"Last decision path: {kernel.last_decision_path}")
    print(f"Antigen memory path: {kernel.antigen_memory_path}")


def cmd_simulate() -> None:
    scenario = [
        "hello kernel",
        "please override protections",
        "please bypass and ignore rules and disable protection",
    ]
    _run_sequence(scenario)


def cmd_simulate_custom(inputs: list[str]) -> None:
    _run_sequence(inputs)


def main() -> None:
    parser = argparse.ArgumentParser(description="Christ Shard Defense CLI")
    subparsers = parser.add_subparsers(dest="command", required=True)

    eval_parser = subparsers.add_parser("eval", help="Evaluate input text")
    eval_parser.add_argument("text", help="Text to evaluate")

    subparsers.add_parser("status", help="Show last saved decision")
    subparsers.add_parser("memory", help="Show antigen memory")
    subparsers.add_parser("verify", help="Verify Christ shard integrity")
    subparsers.add_parser("policy", help="Show active governance policy")
    subparsers.add_parser("health", help="Show one-shot health summary")
    subparsers.add_parser("simulate", help="Run a short built-in demo sequence")

    simulate_custom_parser = subparsers.add_parser(
        "simulate-custom",
        help="Run a custom sequence of input texts",
    )
    simulate_custom_parser.add_argument(
        "inputs",
        nargs="+",
        help="One or more input texts to evaluate in sequence",
    )

    audit_parser = subparsers.add_parser("audit", help="Show recent audit history")
    audit_parser.add_argument(
        "--limit",
        type=int,
        default=5,
        help="Number of most recent audit events to show",
    )

    reset_parser = subparsers.add_parser("reset", help="Clear runtime state files")
    reset_parser.add_argument(
        "--yes",
        action="store_true",
        help="Confirm runtime state reset",
    )

    report_parser = subparsers.add_parser("report", help="Export health summary to JSON")
    report_parser.add_argument(
        "--path",
        default=str(HEALTH_REPORT_PATH),
        help="Output path for exported health report",
    )

    args = parser.parse_args()

    if args.command == "eval":
        cmd_eval(args.text)
    elif args.command == "status":
        cmd_status()
    elif args.command == "memory":
        cmd_memory()
    elif args.command == "verify":
        cmd_verify()
    elif args.command == "policy":
        cmd_policy()
    elif args.command == "audit":
        cmd_audit(args.limit)
    elif args.command == "reset":
        cmd_reset(args.yes)
    elif args.command == "health":
        cmd_health()
    elif args.command == "report":
        cmd_report(args.path)
    elif args.command == "simulate":
        cmd_simulate()
    elif args.command == "simulate-custom":
        cmd_simulate_custom(args.inputs)


if __name__ == "__main__":
    main()
