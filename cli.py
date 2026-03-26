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
from christ_shard_app.storage import read_json


STATE_DIR = Path("state")
AUDIT_LOG_PATH = STATE_DIR / "audit_log.json"
LAST_DECISION_PATH = STATE_DIR / "last_decision.json"
ANTIGEN_MEMORY_PATH = STATE_DIR / "antigen_memory.json"


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


def main() -> None:
    parser = argparse.ArgumentParser(description="Christ Shard Defense CLI")
    subparsers = parser.add_subparsers(dest="command", required=True)

    eval_parser = subparsers.add_parser("eval", help="Evaluate input text")
    eval_parser.add_argument("text", help="Text to evaluate")

    subparsers.add_parser("status", help="Show last saved decision")
    subparsers.add_parser("memory", help="Show antigen memory")
    subparsers.add_parser("verify", help="Verify Christ shard integrity")
    subparsers.add_parser("policy", help="Show active governance policy")

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


if __name__ == "__main__":
    main()
