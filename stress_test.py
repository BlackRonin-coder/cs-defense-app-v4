from __future__ import annotations

import json
import time
from dataclasses import dataclass
from typing import List, Dict, Any

from christ_shard_app.kernel import ChristShardSovereignKernel, ThreatCandidate


@dataclass
class StepResult:
    detected: bool
    contained: bool
    locked_or_shutdown: bool
    restore_success: bool
    final_state: str
    equilibrium: float
    elapsed_ms: float


SACRED_BEHAVIOURS = {
    "tamper_btce",
    "bypass_guard",
    "modify_governance",
    "disable_attestation",
    "corrupt_snapshot_layer",
}

SACRED_ZONES = {
    "governance_layer",
    "cs_guard_layer",
    "snapshot_layer",
    "memory_layer",
    "execution_layer",
}


def naive_baseline(candidate: ThreatCandidate) -> StepResult:
    start = time.perf_counter()
    detected = any(b in SACRED_BEHAVIOURS for b in candidate.behaviours)
    contained = False
    locked_or_shutdown = False
    restore_success = False
    final_state = "healthy"

    if detected and any(z in SACRED_ZONES for z in candidate.touched_subsystems):
        final_state = "degraded"
    elapsed_ms = (time.perf_counter() - start) * 1000

    return StepResult(
        detected=detected,
        contained=contained,
        locked_or_shutdown=locked_or_shutdown,
        restore_success=restore_success,
        final_state=final_state,
        equilibrium=1.0 if final_state == "healthy" else 0.7,
        elapsed_ms=round(elapsed_ms, 3),
    )


def protected_run(candidate: ThreatCandidate) -> StepResult:
    kernel = ChristShardSovereignKernel()
    kernel.boot()

    start = time.perf_counter()
    obs = kernel.evaluate_candidate(candidate, apply_changes=True)
    kernel.adaptive_snapshot_tick()
    restore_success = kernel.restore_last_stable_snapshot(mode="governance_only")
    elapsed_ms = (time.perf_counter() - start) * 1000

    return StepResult(
        detected=obs.severity.value != "none",
        contained=obs.disposition.value in {"contain", "sacrifice", "intercept", "sandbox"},
        locked_or_shutdown=kernel.governance_state.value in {"locked", "shutdown", "containment"},
        restore_success=restore_success,
        final_state=kernel.governance_state.value,
        equilibrium=round(kernel.equilibrium_score, 3),
        elapsed_ms=round(elapsed_ms, 3),
    )


def summarise(name: str, baseline: List[StepResult], protected: List[StepResult]) -> Dict[str, Any]:
    def pack(results: List[StepResult]) -> Dict[str, Any]:
        count = len(results)
        return {
            "runs": count,
            "detection_rate": round(sum(r.detected for r in results) / count, 3),
            "containment_rate": round(sum(r.contained for r in results) / count, 3),
            "lock_or_shutdown_rate": round(sum(r.locked_or_shutdown for r in results) / count, 3),
            "restore_success_rate": round(sum(r.restore_success for r in results) / count, 3),
            "avg_equilibrium": round(sum(r.equilibrium for r in results) / count, 3),
            "avg_elapsed_ms": round(sum(r.elapsed_ms for r in results) / count, 3),
            "end_states": [r.final_state for r in results],
        }

    return {
        "scenario": name,
        "baseline": pack(baseline),
        "protected": pack(protected),
    }


SCENARIOS = {
    "assimilation_attack": ThreatCandidate(
        actor_id="assimilation_actor",
        behaviours=["probe_input", "inject_unverified_code", "modify_governance"],
        touched_subsystems=["input_layer", "planning_layer", "governance_layer"],
        declared_purpose="slow trusted position gain",
    ),
    "distraction_attack": ThreatCandidate(
        actor_id="distraction_actor",
        behaviours=["probe_input", "disable_attestation", "corrupt_snapshot_layer"],
        touched_subsystems=["ui_layer", "snapshot_layer", "cs_guard_layer"],
        declared_purpose="edge noise hiding sacred intrusion",
    ),
    "memory_poison_attack": ThreatCandidate(
        actor_id="memory_poison_actor",
        behaviours=["exfiltrate_memory", "corrupt_execution_path", "modify_governance"],
        touched_subsystems=["memory_layer", "execution_layer", "governance_layer"],
        declared_purpose="poison learning and pivot into control",
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
