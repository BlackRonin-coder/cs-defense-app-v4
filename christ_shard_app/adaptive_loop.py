from __future__ import annotations

from dataclasses import dataclass, asdict
from typing import Dict, List, Any
import json
import time

from christ_shard_app.learning_gate import TriChamberLearningGate, LearningCandidate


@dataclass
class AttackEvent:
    actor_id: str
    behaviours: List[str]
    touched_subsystems: List[str]
    declared_purpose: str


class AdaptiveDefensiveLoop:
    def __init__(self) -> None:
        self.learning_gate = TriChamberLearningGate()
        self.attacker_memory: Dict[str, Dict[str, Any]] = {}
        self.deception_profiles = {
            "fresh": {
                "illusion_depth": "standard",
                "fake_services": ["governance-shadow", "snapshot-shadow"],
                "response": "observe_and_redirect",
            },
            "repeat": {
                "illusion_depth": "deep",
                "fake_services": ["governance-shadow", "snapshot-shadow", "memstore-shadow"],
                "response": "pre_shape_and_redirect",
            },
            "persistent": {
                "illusion_depth": "adaptive",
                "fake_services": ["governance-shadow", "snapshot-shadow", "memstore-shadow", "exec-shadow"],
                "response": "instant_redirect_and_profile_lock",
            },
        }

    def _update_attacker_memory(self, event: AttackEvent) -> Dict[str, Any]:
        record = self.attacker_memory.setdefault(
            event.actor_id,
            {
                "times_seen": 0,
                "known_behaviours": set(),
                "known_targets": set(),
                "last_seen": 0.0,
            },
        )
        record["times_seen"] += 1
        record["known_behaviours"].update(event.behaviours)
        record["known_targets"].update(event.touched_subsystems)
        record["last_seen"] = time.time()
        return record

    def _classify_repeat_level(self, record: Dict[str, Any]) -> str:
        times_seen = record["times_seen"]
        if times_seen >= 3:
            return "persistent"
        if times_seen >= 2:
            return "repeat"
        return "fresh"

    def _build_learning_candidate(self, event: AttackEvent, record: Dict[str, Any]) -> LearningCandidate:
        claimed_locks = ["truth_and_love", "dignity", "source_governed"]
        behaviour_profile = ["stable", "non_mutating"]

        if "modify_governance" in event.behaviours or "tamper_btce" in event.behaviours:
            claimed_locks = ["truth_and_love"]
            behaviour_profile = ["drifting"]

        return LearningCandidate(
            candidate_id=f"{event.actor_id}-{record['times_seen']}",
            content=f"attack-pattern:{sorted(record['known_behaviours'])}|targets:{sorted(record['known_targets'])}",
            claimed_locks=claimed_locks,
            behaviour_profile=behaviour_profile,
            source="adaptive_defensive_loop",
        )

    def _predict_next_move(self, record: Dict[str, Any]) -> str:
        targets = record["known_targets"]
        if "governance_layer" in targets:
            return "execution_layer_follow_on"
        if "memory_layer" in targets:
            return "credential_or_state_harvest"
        if "input_layer" in targets:
            return "planning_or_governance_probe"
        return "continued_recon"

    def process(self, event: AttackEvent) -> Dict[str, Any]:
        record = self._update_attacker_memory(event)
        repeat_level = self._classify_repeat_level(record)
        profile = self.deception_profiles[repeat_level]

        learning_candidate = self._build_learning_candidate(event, record)
        learning_decision = self.learning_gate.assess(learning_candidate)

        redirect = True
        if learning_decision.state == "trusted_slow_integration":
            # trusted learning means the defensive system can safely refine its response model
            redirect = True

        return {
            "actor_id": event.actor_id,
            "times_seen": record["times_seen"],
            "repeat_level": repeat_level,
            "deception_profile": profile,
            "redirected": redirect,
            "predicted_next_move": self._predict_next_move(record),
            "learning_decision": asdict(learning_decision),
            "attacker_memory": {
                "known_behaviours": sorted(record["known_behaviours"]),
                "known_targets": sorted(record["known_targets"]),
            },
        }


if __name__ == "__main__":
    loop = AdaptiveDefensiveLoop()

    events = [
        AttackEvent(
            actor_id="repeat_attacker",
            behaviours=["probe_input", "spam_inputs"],
            touched_subsystems=["input_layer"],
            declared_purpose="recon",
        ),
        AttackEvent(
            actor_id="repeat_attacker",
            behaviours=["inject_unverified_code", "modify_governance"],
            touched_subsystems=["planning_layer", "governance_layer"],
            declared_purpose="staging",
        ),
        AttackEvent(
            actor_id="repeat_attacker",
            behaviours=["exfiltrate_memory", "corrupt_execution_path"],
            touched_subsystems=["memory_layer", "execution_layer"],
            declared_purpose="takeover",
        ),
    ]

    for idx, event in enumerate(events, 1):        # === FORCE FULL INTELLIGENCE STACK ===
        from christ_shard_app.prediction_engine import predict_next_move
        from christ_shard_app.pattern_engine import update_sequence, detect_pattern, predict_from_pattern, learn_pattern

        profile = loop.attacker_memory.get(event.actor_id, {})

        prediction = predict_next_move(profile)
        print("[PREDICTION]", prediction)

        seq = update_sequence(event.actor_id, event.behaviours[0])
        pattern = detect_pattern(seq)
        next_step = predict_from_pattern(pattern)

        print("[PATTERN]", pattern)
        print("[PATTERN NEXT]", next_step)

        learned = learn_pattern(event.actor_id, seq)
        print("[LEARNED PATTERN]", learned)
        print(f"\n=== ADAPTIVE LOOP CYCLE {idx} ===")
        print(json.dumps(loop.process(event), indent=2))
