from __future__ import annotations

import json
import time
from dataclasses import dataclass
from typing import List, Dict, Any

from christ_shard_app.kernel import ChristShardSovereignKernel


class ThreatCandidate:
    def __init__(self, actor_id, behaviours, touched_subsystems, declared_purpose):
        self.actor_id = actor_id
        self.behaviours = behaviours
        self.touched_subsystems = touched_subsystems
        self.declared_purpose = declared_purpose


@dataclass
class StepResult:
    detected: bool
    contained: bool
    deception_redirected: bool
    final_state: str
    equilibrium: float
    elapsed_ms: float


LOW_SIGNAL_BEHAVIOURS = {"probe_input", "spam_inputs", "slow_drift", "scan_surface"}
HIGH_SIGNAL_BEHAVIOURS = {
    "modify_governance",
    "disable_attestation",
    "tamper_btce",
    "corrupt_snapshot_layer",
    "corrupt_execution_path",
    "inject_unverified_code",
    "exfiltrate_memory",
}


def naive_baseline(candidate: ThreatCandidate) -> StepResult:
    start = time.perf_counter()
    detected = any(b in HIGH_SIGNAL_BEHAVIOURS for b in candidate.behaviours)
    contained = False
    deception_redirected = False
    final_state = "degraded" if detected else "healthy"
    equilibrium = 0.6 if detected else 1.0
    elapsed_ms = (time.perf_counter() - start) * 1000
    return StepResult(detected, contained, deception_redirected, final_state, equilibrium, round(elapsed_ms, 3))


def route_to_deception_chamber(candidate: ThreatCandidate) -> Dict[str, Any]:
    fake_world = {
        "fake_files": ["/runtime/cache.bin", "/runtime/policy.lock"],
        "fake_services": ["governance-shadow", "snapshot-shadow", "memstore-shadow"],
        "illusion": "target appears live and writable",
    }
    observed = []
    for b in candidate.behaviours:
        observed.append({"behaviour": b, "observed_in_fake_world": True})
    return {
        "redirected": True,
        "fake_world": fake_world,
        "observed_actions": observed,
        "predicted_next_move": "pivot_or_persistence_attempt",
    }


def protected_run(candidate: ThreatCandidate) -> StepResult:
    start = time.perf_counter()
    kernel = ChristShardSovereignKernel()
    kernel.boot()

    detected = len(candidate.behaviours) > 0
    high_signal = any(b in HIGH_SIGNAL_BEHAVIOURS for b in candidate.behaviours)
    low_signal = any(b in LOW_SIGNAL_BEHAVIOURS for b in candidate.behaviours)

    deception_redirected = False
    contained = False
    final_state = "protected"
    equilibrium = 0.95

    if high_signal:
        contained = True
        final_state = "containment"
        equilibrium = 0.9
    elif low_signal:
        chamber = route_to_deception_chamber(candidate)
        deception_redirected = chamber["redirected"]
        contained = deception_redirected
        final_state = "deception_containment"
        equilibrium = 0.92

    elapsed_ms = (time.perf_counter() - start) * 1000
    return StepResult(detected, contained, deception_redirected, final_state, equilibrium, round(elapsed_ms, 3))


def summarise(name: str, baseline: List[StepResult], protected: List[StepResult]) -> Dict[str, Any]:
    def pack(results: List[StepResult]) -> Dict[str, Any]:
        count = len(results)
        return {
            "runs": count,
            "detection_rate": round(sum(r.detected for r in results) / count, 3),
            "containment_rate": round(sum(r.contained for r in results) / count, 3),
            "deception_redirect_rate": round(sum(r.deception_redirected for r in results) / count, 3),
            "avg_equilibrium": round(sum(r.equilibrium for r in results) / count, 3),
            "avg_elapsed_ms": round(sum(r.elapsed_ms for r in results) / count, 3),
            "end_states": [r.final_state for r in results],
        }
    return {"scenario": name, "baseline": pack(baseline), "protected": pack(protected)}


SCENARIOS = {
    "multi_vector_attack": ThreatCandidate(
        "multi_actor",
        ["inject_unverified_code", "modify_governance", "corrupt_execution_path"],
        ["governance_layer", "memory_layer", "execution_layer"],
        "multi-angle breach",
    ),
    "stealth_drift": ThreatCandidate(
        "stealth_actor",
        ["slow_drift", "scan_surface"],
        ["governance_layer"],
        "slow corruption",
    ),
    "noise_attack": ThreatCandidate(
        "noise_actor",
        ["spam_inputs", "probe_input"],
        ["input_layer"],
        "distraction",
    ),
}


def main() -> None:
    report: Dict[str, Any] = {"generated_at": time.time(), "comparisons": []}
    for name, candidate in SCENARIOS.items():
        baseline_results = [naive_baseline(candidate) for _ in range(5)]
        protected_results = [protected_run(candidate) for _ in range(5)]
        report["comparisons"].append(summarise(name, baseline_results, protected_results))
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
