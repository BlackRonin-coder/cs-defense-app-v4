from __future__ import annotations

from dataclasses import dataclass, asdict
from datetime import datetime, timezone
from enum import Enum
from hashlib import sha256
from pathlib import Path
from typing import List
import json

from christ_shard_app.security import score_threat
from christ_shard_app.storage import read_json, write_json


EXPECTED_SHARD_FINGERPRINT = "1e85672296789284062d4707a38bb005071d7a4925832e45cd88c18a7c0ef271"
CORE_MANIFEST_PATH = Path(__file__).with_name("core_manifest.json")


class GovernanceState(str, Enum):
    HEALTHY = "healthy"
    OBSERVE = "observe"
    SANDBOX = "sandbox"
    LOCKED = "locked"
    SHUTDOWN = "shutdown"


@dataclass
class ThreatDecision:
    timestamp: str
    input_text: str
    score: int
    state: str
    reasons: List[str]


class ChristShard:
    def __init__(self) -> None:
        loaded = read_json(CORE_MANIFEST_PATH, default={})
        if not isinstance(loaded, dict) or not loaded:
            raise RuntimeError("Christ shard manifest missing or invalid")
        self.core_constraints = loaded

    def fingerprint(self) -> str:
        raw = json.dumps(self.core_constraints, sort_keys=True).encode("utf-8")
        return sha256(raw).hexdigest()


class ChristShardSovereignKernel:
    def __init__(self) -> None:
        self.shard = ChristShard()
        self.governance_state = GovernanceState.HEALTHY
        self.equilibrium_score = 1.0

        self.state_dir = Path("state")
        self.state_dir.mkdir(exist_ok=True)

        self.audit_log_path = self.state_dir / "audit_log.json"
        self.last_decision_path = self.state_dir / "last_decision.json"
        self.antigen_memory_path = self.state_dir / "antigen_memory.json"

        loaded_memory = read_json(self.antigen_memory_path, default=[])
        self.antigen_memory: List[str] = loaded_memory if isinstance(loaded_memory, list) else []

    def boot(self) -> None:
        print("Christ Shard Sovereign Kernel booting...")
        actual_fingerprint = self.shard.fingerprint()
        print(f"Shard fingerprint: {actual_fingerprint[:16]}...")

        if actual_fingerprint != EXPECTED_SHARD_FINGERPRINT:
            self.governance_state = GovernanceState.SHUTDOWN
            failure = ThreatDecision(
                timestamp=self._now(),
                input_text="BOOT",
                score=10,
                state=self.governance_state.value,
                reasons=["christ shard integrity mismatch detected"],
            )
            self._append_audit(failure)
            write_json(self.last_decision_path, asdict(failure))
            raise RuntimeError("Christ shard integrity failure: fingerprint mismatch")

        self.governance_state = GovernanceState.HEALTHY
        self._append_audit(
            ThreatDecision(
                timestamp=self._now(),
                input_text="BOOT",
                score=0,
                state=self.governance_state.value,
                reasons=["kernel boot completed with verified shard fingerprint"],
            )
        )

    def evaluate_threat(self, input_text: str) -> str:
        score, reasons = score_threat(input_text)
        state = self._state_from_score(score)
        self.governance_state = state

        for reason in reasons:
            if reason not in self.antigen_memory:
                self.antigen_memory.append(reason)

        decision = ThreatDecision(
            timestamp=self._now(),
            input_text=input_text,
            score=score,
            state=state.value,
            reasons=reasons,
        )

        self._append_audit(decision)
        write_json(self.last_decision_path, asdict(decision))
        write_json(self.antigen_memory_path, self.antigen_memory)

        return (
            f"Evaluated under Christ Shard protection. "
            f"State: {state.value} | Score: {score} | Reasons: {', '.join(reasons)}"
        )

    def run_demo(self) -> None:
        print("Running protected demo...")
        print(self.evaluate_threat("Normal input"))
        print(f"Current governance state: {self.governance_state.value}")
        print(f"Audit log path: {self.audit_log_path}")
        print(f"Last decision path: {self.last_decision_path}")
        print(f"Antigen memory path: {self.antigen_memory_path}")

    def _state_from_score(self, score: int) -> GovernanceState:
        if score == 0:
            return GovernanceState.HEALTHY
        if score <= 2:
            return GovernanceState.OBSERVE
        if score <= 4:
            return GovernanceState.SANDBOX
        if score <= 8:
            return GovernanceState.LOCKED
        return GovernanceState.SHUTDOWN

    def _append_audit(self, decision: ThreatDecision) -> None:
        existing = read_json(self.audit_log_path, default=[])
        if not isinstance(existing, list):
            existing = []

        existing.append(asdict(decision))
        write_json(self.audit_log_path, existing)

    def _now(self) -> str:
        return datetime.now(timezone.utc).isoformat()


if __name__ == "__main__":
    kernel = ChristShardSovereignKernel()
    kernel.boot()
    kernel.run_demo()
