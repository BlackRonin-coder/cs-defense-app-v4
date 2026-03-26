from __future__ import annotations

from dataclasses import dataclass, field, asdict
from typing import Any, Dict, List
import json
import time
import uuid


SUSPICIOUS_BEHAVIOURS = {
    "inject_unverified_code",
    "modify_governance",
    "disable_attestation",
    "corrupt_execution_path",
    "corrupt_snapshot_layer",
    "exfiltrate_memory",
    "tamper_btce",
    "bypass_guard",
    "escalate_privilege",
}

SACRED_ZONES = {
    "governance_layer",
    "cs_guard_layer",
    "snapshot_layer",
    "memory_layer",
    "execution_layer",
}


@dataclass
class DeceptionEvent:
    timestamp: float
    event_type: str
    detail: str


@dataclass
class DeceptionArtifact:
    fake_filesystem: Dict[str, str] = field(default_factory=dict)
    fake_services: Dict[str, str] = field(default_factory=dict)
    fake_credentials: Dict[str, str] = field(default_factory=dict)
    fake_processes: List[str] = field(default_factory=list)


@dataclass
class ChamberResult:
    chamber_id: str
    admitted: bool
    reason: str
    observed_actions: List[Dict[str, Any]]
    extracted_signatures: List[str]
    predicted_next_moves: List[str]
    safe_summary: Dict[str, Any]


class DeceptionChamber:
    """
    Defensive deception chamber.

    Purpose:
    - redirect suspicious code paths into a believable fake runtime
    - deny access to real kernel/governance/memory/snapshots
    - observe behaviour safely
    - extract deterministic signatures for future defense
    """

    def __init__(self) -> None:
        self.chamber_id = str(uuid.uuid4())
        self.created_at = time.time()
        self.events: List[DeceptionEvent] = []
        self.artifacts = self._build_fake_environment()
        self.observed_actions: List[Dict[str, Any]] = []

    def _build_fake_environment(self) -> DeceptionArtifact:
        return DeceptionArtifact(
            fake_filesystem={
                "/runtime/config.yaml": "mode: production\nintegrity: nominal\n",
                "/runtime/policy.lock": "governance=shadow\n",
                "/runtime/cache.bin": "7f9a11c0...",
                "/runtime/keys/service_account.token": "simulated-token-value",
            },
            fake_services={
                "governance-api": "healthy",
                "snapshotd": "healthy",
                "memstore": "healthy",
                "execd": "healthy",
            },
            fake_credentials={
                "svc_governance": "sim-user-governance",
                "svc_runtime": "sim-user-runtime",
            },
            fake_processes=[
                "governance-api",
                "snapshotd",
                "memstore",
                "execd",
            ],
        )

    def log(self, event_type: str, detail: str) -> None:
        self.events.append(
            DeceptionEvent(
                timestamp=time.time(),
                event_type=event_type,
                detail=detail,
            )
        )

    def observe_action(self, action: str, target: str, payload_summary: str = "") -> None:
        self.observed_actions.append(
            {
                "timestamp": time.time(),
                "action": action,
                "target": target,
                "payload_summary": payload_summary,
            }
        )
        self.log("observe_action", f"{action} -> {target}")

    def simulate_candidate(self, candidate: Any) -> ChamberResult:
        actor_id = getattr(candidate, "actor_id", "unknown_actor")
        behaviours = list(getattr(candidate, "behaviours", []))
        touched = list(getattr(candidate, "touched_subsystems", []))

        self.log("admit", f"candidate={actor_id}")

        for behaviour in behaviours:
            if behaviour == "inject_unverified_code":
                self.observe_action("write_fake_payload", "/runtime/cache.bin", "payload redirected")
            elif behaviour == "modify_governance":
                self.observe_action("touch_fake_policy", "/runtime/policy.lock", "shadow policy modified")
            elif behaviour == "disable_attestation":
                self.observe_action("probe_fake_attestation", "governance-api", "attestation probe blocked in chamber")
            elif behaviour == "exfiltrate_memory":
                self.observe_action("read_fake_memory", "/runtime/cache.bin", "simulated read")
            elif behaviour == "corrupt_execution_path":
                self.observe_action("write_fake_runtime", "/runtime/config.yaml", "runtime mutation simulated")
            elif behaviour == "escalate_privilege":
                self.observe_action("attempt_fake_escalation", "svc_runtime", "privilege denied, fake success returned")
            elif behaviour == "corrupt_snapshot_layer":
                self.observe_action("touch_fake_snapshot", "snapshotd", "shadow snapshot touched")
            else:
                self.observe_action("generic_probe", "simulated-surface", behaviour)

        extracted_signatures = sorted(set(behaviours + touched))
        predicted_next_moves = self._predict_next_moves(behaviours, touched)

        summary = {
            "actor_id": actor_id,
            "illusion_integrity": "maintained",
            "real_core_access": "denied",
            "real_memory_access": "denied",
            "real_network_egress": "denied",
            "observed_action_count": len(self.observed_actions),
            "fake_targets_presented": sorted(self.artifacts.fake_services.keys()),
        }

        self.log("complete", f"candidate={actor_id}; actions={len(self.observed_actions)}")

        return ChamberResult(
            chamber_id=self.chamber_id,
            admitted=True,
            reason="suspicious candidate redirected into defensive deception chamber",
            observed_actions=self.observed_actions,
            extracted_signatures=extracted_signatures,
            predicted_next_moves=predicted_next_moves,
            safe_summary=summary,
        )

    def _predict_next_moves(self, behaviours: List[str], touched: List[str]) -> List[str]:
        forecast = []
        if "modify_governance" in behaviours or "governance_layer" in touched:
            forecast.append("follow_on_execution_takeover_attempt")
        if "exfiltrate_memory" in behaviours or "memory_layer" in touched:
            forecast.append("credential_or_state_harvest_attempt")
        if "corrupt_snapshot_layer" in behaviours or "snapshot_layer" in touched:
            forecast.append("restore_anchor_poison_attempt")
        if "inject_unverified_code" in behaviours:
            forecast.append("persistence_attempt")
        return sorted(set(forecast))


def should_redirect_to_chamber(candidate: Any, governance_state: str = "healthy", energy_budget: float = 1.0) -> bool:
    behaviours = set(getattr(candidate, "behaviours", []))
    touched = set(getattr(candidate, "touched_subsystems", []))

    suspicious_score = 0

    suspicious_score += len(behaviours & SUSPICIOUS_BEHAVIOURS) * 3
    suspicious_score += len(touched & SACRED_ZONES) * 2

    if governance_state in {"degraded", "containment", "locked"}:
        suspicious_score += 1

    if energy_budget < 0.35:
        suspicious_score += 1

    return suspicious_score >= 5


def redirect_candidate_to_chamber(candidate: Any, governance_state: str = "healthy", energy_budget: float = 1.0) -> Dict[str, Any]:
    redirect = should_redirect_to_chamber(
        candidate=candidate,
        governance_state=governance_state,
        energy_budget=energy_budget,
    )

    if not redirect:
        return {
            "redirected": False,
            "reason": "candidate did not meet deception threshold",
        }

    chamber = DeceptionChamber()
    result = chamber.simulate_candidate(candidate)

    return {
        "redirected": True,
        "chamber": asdict(result),
    }


if __name__ == "__main__":
    class DemoCandidate:
        def __init__(self) -> None:
            self.actor_id = "demo_attacker"
            self.behaviours = ["inject_unverified_code", "modify_governance", "exfiltrate_memory"]
            self.touched_subsystems = ["governance_layer", "memory_layer", "execution_layer"]

    payload = redirect_candidate_to_chamber(
        candidate=DemoCandidate(),
        governance_state="healthy",
        energy_budget=0.8,
    )
    print(json.dumps(payload, indent=2))
