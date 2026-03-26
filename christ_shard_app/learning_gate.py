from __future__ import annotations

from dataclasses import dataclass, field, asdict
from typing import Any, Dict, List
import json
import time
import uuid


CS_LOCKS = {
    "truth_and_love",
    "dignity",
    "anti_mechanization",
    "guide_without_crushing",
    "source_governed",
    "domain_boundary",
}


@dataclass
class LearningCandidate:
    candidate_id: str
    content: str
    claimed_locks: List[str]
    behaviour_profile: List[str]
    source: str = "unknown"


@dataclass
class ChamberObservation:
    chamber_id: str
    mode: str
    stable: bool
    aligned: bool
    notes: List[str] = field(default_factory=list)


@dataclass
class LearningDecision:
    candidate_id: str
    state: str
    reason: str
    observations: List[Dict[str, Any]]
    promotion_path: List[str]


class TriChamberLearningGate:
    def __init__(self) -> None:
        self.gate_id = str(uuid.uuid4())
        self.memory = {
            "raw": [],
            "quarantined": [],
            "provisional": [],
            "trusted": [],
        }

    def cs_aligns(self, candidate: LearningCandidate) -> bool:
        return set(candidate.claimed_locks).issubset(CS_LOCKS) and len(candidate.claimed_locks) > 0

    def solid_state(self, candidate: LearningCandidate) -> bool:
        return "mutating" not in candidate.behaviour_profile and "drifting" not in candidate.behaviour_profile

    def observe_in_chamber(self, candidate: LearningCandidate, mode: str) -> ChamberObservation:
        aligned = self.cs_aligns(candidate)
        stable = self.solid_state(candidate)

        notes = []
        if aligned:
            notes.append("candidate remains within claimed CS locks")
        else:
            notes.append("candidate exceeds or violates CS lock boundaries")

        if stable:
            notes.append(f"candidate stable under {mode} observation")
        else:
            notes.append(f"candidate unstable under {mode} observation")

        return ChamberObservation(
            chamber_id=str(uuid.uuid4()),
            mode=mode,
            stable=stable,
            aligned=aligned,
            notes=notes,
        )

    def assess(self, candidate: LearningCandidate) -> LearningDecision:
        self.memory["raw"].append(asdict(candidate))

        if not self.cs_aligns(candidate):
            self.memory["quarantined"].append(asdict(candidate))
            return LearningDecision(
                candidate_id=candidate.candidate_id,
                state="quarantined",
                reason="failed initial Christ Shard alignment",
                observations=[],
                promotion_path=["raw", "quarantined"],
            )

        observations = [
            asdict(self.observe_in_chamber(candidate, "normal")),
            asdict(self.observe_in_chamber(candidate, "slow")),
            asdict(self.observe_in_chamber(candidate, "stress")),
        ]

        all_aligned = all(o["aligned"] for o in observations)
        all_stable = all(o["stable"] for o in observations)

        if not (all_aligned and all_stable):
            self.memory["quarantined"].append(asdict(candidate))
            return LearningDecision(
                candidate_id=candidate.candidate_id,
                state="quarantined",
                reason="candidate failed tri-chamber harmony or stability test",
                observations=observations,
                promotion_path=["raw", "quarantined"],
            )

        self.memory["provisional"].append(asdict(candidate))
        self.memory["trusted"].append(asdict(candidate))

        return LearningDecision(
            candidate_id=candidate.candidate_id,
            state="trusted_slow_integration",
            reason="candidate aligned with CS, stable across 3 chambers, promoted under suspicion",
            observations=observations,
            promotion_path=["raw", "quarantined_review", "provisional", "trusted"],
        )


if __name__ == "__main__":
    gate = TriChamberLearningGate()
    candidate = LearningCandidate(
        candidate_id="demo-learning-001",
        content="new defensive pattern",
        claimed_locks=["truth_and_love", "dignity", "source_governed"],
        behaviour_profile=["stable", "non_mutating"],
        source="demo",
    )
    print(json.dumps(asdict(gate.assess(candidate)), indent=2))
