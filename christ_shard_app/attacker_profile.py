from __future__ import annotations

from dataclasses import dataclass, asdict
from typing import Dict, List, Any
import json


@dataclass
class AttackerProfile:
    actor_id: str
    attempts: int
    threat_score: int
    known_behaviours: List[str]
    known_targets: List[str]
    risk_level: str


class AttackerProfiler:
    def __init__(self) -> None:
        self.profiles: Dict[str, Dict[str, Any]] = {}

    def _risk_level(self, score: int) -> str:
        if score >= 15:
            return "critical"
        if score >= 10:
            return "high"
        if score >= 5:
            return "medium"
        return "low"

    def update_profile(self, actor_id: str, behaviours: List[str], targets: List[str]) -> Dict[str, Any]:
        record = self.profiles.setdefault(
            actor_id,
            {
                "actor_id": actor_id,
                "attempts": 0,
                "threat_score": 0,
                "known_behaviours": set(),
                "known_targets": set(),
            },
        )

        record["attempts"] += 1
        record["known_behaviours"].update(behaviours)
        record["known_targets"].update(targets)

        record["threat_score"] += len(behaviours) * 2
        if "governance_layer" in targets:
            record["threat_score"] += 4
        if "memory_layer" in targets:
            record["threat_score"] += 3
        if "execution_layer" in targets:
            record["threat_score"] += 3

        risk_level = self._risk_level(record["threat_score"])

        profile = AttackerProfile(
            actor_id=record["actor_id"],
            attempts=record["attempts"],
            threat_score=record["threat_score"],
            known_behaviours=sorted(record["known_behaviours"]),
            known_targets=sorted(record["known_targets"]),
            risk_level=risk_level,
        )

        return asdict(profile)


if __name__ == "__main__":
    profiler = AttackerProfiler()
    print(json.dumps(profiler.update_profile(
        "demo_attacker",
        ["probe_input", "modify_governance"],
        ["input_layer", "governance_layer"]
    ), indent=2))
