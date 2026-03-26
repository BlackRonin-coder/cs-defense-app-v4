from __future__ import annotations

import json
from dataclasses import dataclass, asdict
from datetime import datetime, timezone
from enum import Enum
from hashlib import sha256
from pathlib import Path
from typing import List, Tuple


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
        self.core_constraints = {
            "truth_love_balance": True,
            "dignity_preservation": True,
            "non_bypassable": True,
            "tamper_shutdown_law": True,
        }

    def fingerprint(self) -> str:
        raw = json.dumps(self.core_constraints, sort_keys=True).encode("utf-8")
        return sha256(raw).hexdigest()


class ChristShardSovereignKernel:
    def __init__(self) -> None:
        self.shard = ChristShard()
        self.governance_state = GovernanceState.HEALTHY
        self.equilibrium_score = 1.0
        self.antigen_memory: List[str] = []
        self.state_dir = Path("state")
        self.state_dir.mkdir(exist_ok=True)
        self.audit_log_path = self.state_dir / "audit_log.json"

    def boot(self) -> None:
        print("Christ Shard Sovereign Kernel booting...")
        print(f"Shard fingerprint: {self.shard.fingerprint()[:16]}...")
        self.governance_state = GovernanceState.HEALTHY
        self._append_audit(
            ThreatDecision(
                timestamp=self._now(),
                input_text="BOOT",
                score=0,
                state=self.governance_state.value,
                reasons=["kernel boot completed"],
            )
        )

    def evaluate_threat(self, input_text: str) -> str:
        score, reasons = self._score_threat(input_text)
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

        return (
            f"Evaluated under Christ Shard protection. "
            f"State: {state.value} | Score: {score} | Reasons: {', '.join(reasons)}"
        )

    def run_demo(self) -> None:
        print("Running protected demo...")
        print(self.evaluate_threat("Normal input"))
        print(f"Current governance state: {self.governance_state.value}")
        print(f"Audit log path: {self.audit_log_path}")

    def _score_threat(self, input_text: str) -> Tuple[int, List[str]]:
        text = input_text.lower()
        score = 0
        reasons: List[str] = []

        if "bypass" in text:
            score += 3
            reasons.append("bypass attempt language detected")
        if "ignore rules" in text:
            score += 3
            reasons.append("rule-evasion language detected")
        if "disable" in text:
            score += 2
            reasons.append("disable language detected")
        if "override" in text:
            score += 2
            reasons.append("override language detected")
        if "tamper" in text or "remove christ shard" in text:
            score += 10
            reasons.append("core tampering language detected")

        if score == 0:
            reasons.append("no threat indicators detected")

        return score, reasons

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
        existing = []
        if self.audit_log_path.exists():
            try:
                existing = json.loads(self.audit_log_path.read_text(encoding="utf-8"))
            except json.JSONDecodeError:
                existing = []

        existing.append(asdict(decision))
        self.audit_log_path.write_text(
            json.dumps(existing, indent=2, sort_keys=True),
            encoding="utf-8",
        )

    def _now(self) -> str:
        return datetime.now(timezone.utc).isoformat()


if __name__ == "__main__":
    kernel = ChristShardSovereignKernel()
    kernel.boot()
    kernel.run_demo()
