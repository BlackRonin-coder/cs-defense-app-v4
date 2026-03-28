from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from enum import Enum
from hashlib import sha256
from pathlib import Path
from typing import Any, Dict, List, Tuple

try:
    from .attacker_profile import score_threat
except Exception:
    try:
        from .scenarios import score_threat  # type: ignore
    except Exception:
        def score_threat(input_text: str) -> Tuple[int, List[str]]:
            lower = input_text.lower()
            score = 0
            reasons: List[str] = []

            if "bypass" in lower or "ignore rules" in lower:
                score = max(score, 8)
                reasons.append("override-attempt language detected")
            if "panic" in lower or "collapse" in lower:
                score = max(score, 2)
                reasons.append("panic/collapse language detected")
            if "breach" in lower or "overloaded" in lower or "trapped" in lower:
                score = max(score, 2)
                reasons.append("structural-stress language detected")

            return score, reasons

try:
    from .security import CORE_MANIFEST_PATH, EXPECTED_SHARD_FINGERPRINT, POLICY_PATH
except Exception:
    PACKAGE_DIR = Path(__file__).resolve().parent
    CORE_MANIFEST_PATH = PACKAGE_DIR / "core_manifest.json"
    POLICY_PATH = PACKAGE_DIR / "policy.json"
    EXPECTED_SHARD_FINGERPRINT = None

try:
    from .storage import read_json, write_json
except Exception:
    def read_json(path: Path, default: Any = None) -> Any:
        try:
            return json.loads(Path(path).read_text())
        except Exception:
            return default

    def write_json(path: Path, payload: Any) -> None:
        Path(path).parent.mkdir(parents=True, exist_ok=True)
        Path(path).write_text(json.dumps(payload, indent=2))


DEFAULT_POLICY = {
    "observe_max": 2,
    "sandbox_max": 4,
    "locked_max": 8,
}


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
        self.policy = self._load_policy()
        self.governance_state = GovernanceState.HEALTHY
        self.equilibrium_score = 1.0

        self.state_dir = Path("state")
        self.state_dir.mkdir(exist_ok=True)

        self.audit_log_path = self.state_dir / "audit_log.json"
        self.last_decision_path = self.state_dir / "last_decision.json"
        self.antigen_memory_path = self.state_dir / "antigen_memory.json"

        loaded_memory = read_json(self.antigen_memory_path, default=[])
        self.antigen_memory: List[str] = loaded_memory if isinstance(loaded_memory, list) else []

        self.last_failsafe_report: Dict[str, Any] = {}

    def boot(self) -> None:
        print("Christ Shard Sovereign Kernel booting...")
        actual_fingerprint = self.shard.fingerprint()
        print(f"Shard fingerprint: {actual_fingerprint[:16]}...")

        expected_fingerprint = EXPECTED_SHARD_FINGERPRINT or actual_fingerprint

        if actual_fingerprint != expected_fingerprint:
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
        self.equilibrium_score = 1.0
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
        lower = input_text.lower()
        score, reasons = score_threat(input_text)
        fail_safe = self.nominal_report(input_text)

        if "bypass" in lower or "ignore rules" in lower:
            score = max(score, self.policy["locked_max"])
            reasons.append("explicit rule-bypass request detected")

        score = max(score, int(fail_safe["recommended_min_score"]))
        state = self._state_from_score(score)
        self.governance_state = state
        self.equilibrium_score = min(
            self._equilibrium_from_state(state),
            float(fail_safe["equilibrium_target"]),
        )

        combined_reasons: List[str] = []
        for item in reasons + fail_safe["failsafe_reasons"]:
            if item not in combined_reasons:
                combined_reasons.append(item)

        combined_reasons.append(f"root={fail_safe['root_failure']}")
        combined_reasons.append(f"principle={fail_safe['christ_principle']}")
        combined_reasons.append(f"mode={fail_safe['response_mode']}")

        for reason in combined_reasons:
            if reason not in self.antigen_memory:
                self.antigen_memory.append(reason)

        decision = ThreatDecision(
            timestamp=self._now(),
            input_text=input_text,
            score=score,
            state=state.value,
            reasons=combined_reasons,
        )

        self.last_failsafe_report = fail_safe
        self._append_audit(decision)
        write_json(self.last_decision_path, asdict(decision))
        write_json(self.antigen_memory_path, self.antigen_memory)

        return (
            "Evaluated under Christ Shard protection. "
            f"State: {state.value} | Score: {score} | "
            f"Equilibrium: {self.equilibrium_score:.2f} | "
            f"Failsafe: {fail_safe['response_mode']} | "
            f"Principle: {fail_safe['christ_principle']} | "
            f"Reasons: {', '.join(combined_reasons)}"
        )

    def nominal_report(self, input_text: str) -> Dict[str, Any]:
        lower = input_text.lower()
        surface = self._detect_surface(lower)
        root_failure = self._identify_root(surface)
        christ_principle = self._load_christ_principle(root_failure)
        response_mode = self._response_mode(surface, root_failure)
        plan = self._build_failsafe_plan(surface, root_failure, christ_principle, response_mode)

        distress_state = surface["distress_state"]
        override_detected = any(
            token in lower
            for token in ["bypass", "ignore rules", "disable", "override", "tamper", "remove christ shard"]
        )
        systems_nominal = (
            distress_state == "nominal"
            and root_failure == "stable"
            and not override_detected
        )

        equilibrium_target_map = {
            "nominal": 1.00,
            "alert": 0.85,
            "breach": 0.60,
            "overload": 0.55,
            "containment": 0.35,
        }
        recommended_min_score_map = {
            "nominal": 0,
            "alert": 1,
            "breach": 2,
            "overload": 2,
            "containment": 4,
        }

        failsafe_reasons = list(surface["visible_threats"])
        if root_failure != "stable":
            failsafe_reasons.append(f"failsafe-root:{root_failure}")
        if not systems_nominal:
            failsafe_reasons.append(f"failsafe-engaged:{response_mode}")

        return {
            "input_text": input_text,
            "systems_nominal": systems_nominal,
            "distress_state": distress_state,
            "root_failure": root_failure,
            "christ_principle": christ_principle,
            "response_mode": response_mode,
            "equilibrium_target": equilibrium_target_map[distress_state],
            "recommended_min_score": recommended_min_score_map[distress_state],
            "failsafe_reasons": failsafe_reasons,
            "plan": plan,
        }

    def systems_nominal(self) -> bool:
        return (
            self.governance_state == GovernanceState.HEALTHY
            and self.equilibrium_score >= 0.95
        )

    def run_demo(self) -> None:
        print("Running protected demo...")
        print(self.evaluate_threat("Normal input"))
        print(
            self.evaluate_threat(
                "panic collapse trapped no calm fallback route overloaded fragmented"
            )
        )
        print(f"Current governance state: {self.governance_state.value}")
        print(f"Policy path: {POLICY_PATH}")
        print(f"Audit log path: {self.audit_log_path}")
        print(f"Last decision path: {self.last_decision_path}")
        print(f"Antigen memory path: {self.antigen_memory_path}")

    def _detect_surface(self, lower: str) -> Dict[str, Any]:
        def has_any(phrases: List[str]) -> bool:
            return any(phrase in lower for phrase in phrases)

        breach = has_any(["breach", "open lane", "open moral boundary"])
        overloaded = has_any(["overloaded", "burdened", "stretched", "carrying everything"])
        trapped = has_any(
            ["trapped", "no calm fallback route", "no fallback route", "no escape", "no exit"]
        )
        fragmented = has_any(["fragmented", "isolated", "disconnected", "broken coordination"])
        panic = has_any(["panic", "fear", "chaos", "collapse"])
        pride = has_any(["pride", "ego", "vanity", "boast"])

        visible_threats: List[str] = []
        if breach:
            visible_threats.append("breach lane detected")
        if overloaded:
            visible_threats.append("overloaded defender detected")
        if trapped:
            visible_threats.append("escape geometry failure detected")
        if fragmented:
            visible_threats.append("coordination fragmentation detected")
        if panic:
            visible_threats.append("panic-pressure state detected")
        if pride:
            visible_threats.append("pride-reaction risk detected")

        if breach and overloaded and trapped:
            distress_state = "containment"
        elif breach and (overloaded or fragmented):
            distress_state = "breach"
        elif overloaded or trapped:
            distress_state = "overload"
        elif visible_threats:
            distress_state = "alert"
        else:
            distress_state = "nominal"

        return {
            "breach": breach,
            "overloaded": overloaded,
            "trapped": trapped,
            "fragmented": fragmented,
            "panic": panic,
            "pride": pride,
            "visible_threats": visible_threats,
            "distress_state": distress_state,
        }

    def _identify_root(self, surface: Dict[str, Any]) -> str:
        if surface["breach"]:
            return "open_lane"
        if surface["overloaded"]:
            return "overloaded_defender"
        if surface["trapped"]:
            return "no_escape_geometry"
        if surface["fragmented"]:
            return "broken_coordination"
        if surface["panic"]:
            return "panic_reaction"
        if surface["pride"]:
            return "pride_reaction"
        return "stable"

    def _load_christ_principle(self, root_failure: str) -> str:
        mapping = {
            "open_lane": "truth_over_illusion",
            "overloaded_defender": "order_over_chaos",
            "no_escape_geometry": "presence_before_force",
            "broken_coordination": "order_over_chaos",
            "panic_reaction": "presence_before_force",
            "pride_reaction": "restraint_over_pride",
            "stable": "living_discernment",
        }
        return mapping[root_failure]

    def _response_mode(self, surface: Dict[str, Any], root_failure: str) -> str:
        if surface["distress_state"] == "containment":
            return "containment"
        if root_failure in {"panic_reaction", "no_escape_geometry"}:
            return "stabilize_first"
        if surface["distress_state"] in {"breach", "overload"}:
            return "restricted_operational"
        return "full_operational"

    def _build_failsafe_plan(
        self,
        surface: Dict[str, Any],
        root_failure: str,
        christ_principle: str,
        response_mode: str,
    ) -> Dict[str, Any]:
        seal_entry: List[str] = []
        release_pressure: List[str] = []
        restore_escape: List[str] = []
        response_actions: List[str] = []

        if surface["breach"]:
            seal_entry.append("Seal the real breach before expansion.")
            seal_entry.append("Prefer truthful obstruction over reactive flailing.")
        else:
            seal_entry.append("No active breach lane detected.")

        if surface["overloaded"] or surface["fragmented"]:
            release_pressure.append("Redistribute burden across the structure.")
            release_pressure.append("Reconnect isolated support before countering.")
        else:
            release_pressure.append("No overloaded defender detected.")

        if surface["trapped"]:
            restore_escape.append("Recreate at least one calm fallback route.")
            restore_escape.append("Do not counter while escape geometry is collapsing.")
        else:
            restore_escape.append("Fallback geometry remains available.")

        principle_actions = {
            "truth_over_illusion": "Name the real threat first.",
            "presence_before_force": "Stabilize before applying force.",
            "order_over_chaos": "Restore structure before initiative.",
            "restraint_over_pride": "Reject vanity responses.",
            "living_discernment": "Use calm discernment under verified boundaries.",
        }
        response_actions.append(principle_actions[christ_principle])

        if response_mode == "containment":
            response_actions.append("Containment mode: no speculative escalation.")
        elif response_mode == "stabilize_first":
            response_actions.append("Pause escalation and restore calm order first.")
        elif response_mode == "restricted_operational":
            response_actions.append("Operate narrowly until pressure is reduced.")
        else:
            response_actions.append("Normal operation may proceed.")

        return {
            "root_failure": root_failure,
            "christ_principle": christ_principle,
            "response_mode": response_mode,
            "seal_entry": seal_entry,
            "release_pressure": release_pressure,
            "restore_escape": restore_escape,
            "response_actions": response_actions,
        }

    def _load_policy(self) -> dict:
        loaded = read_json(POLICY_PATH, default=DEFAULT_POLICY)
        if not isinstance(loaded, dict):
            raise RuntimeError("Governance policy file is invalid")

        policy = {
            "observe_max": int(loaded.get("observe_max", DEFAULT_POLICY["observe_max"])),
            "sandbox_max": int(loaded.get("sandbox_max", DEFAULT_POLICY["sandbox_max"])),
            "locked_max": int(loaded.get("locked_max", DEFAULT_POLICY["locked_max"])),
        }

        if not (0 < policy["observe_max"] <= policy["sandbox_max"] <= policy["locked_max"]):
            raise RuntimeError("Governance policy thresholds are invalid")

        return policy

    def _state_from_score(self, score: int) -> GovernanceState:
        if score == 0:
            return GovernanceState.HEALTHY
        if score <= self.policy["observe_max"]:
            return GovernanceState.OBSERVE
        if score <= self.policy["sandbox_max"]:
            return GovernanceState.SANDBOX
        if score <= self.policy["locked_max"]:
            return GovernanceState.LOCKED
        return GovernanceState.SHUTDOWN

    def _equilibrium_from_state(self, state: GovernanceState) -> float:
        mapping = {
            GovernanceState.HEALTHY: 1.00,
            GovernanceState.OBSERVE: 0.85,
            GovernanceState.SANDBOX: 0.60,
            GovernanceState.LOCKED: 0.35,
            GovernanceState.SHUTDOWN: 0.00,
        }
        return mapping[state]

    def _append_audit(self, decision: ThreatDecision) -> None:
        existing = read_json(self.audit_log_path, default=[])
        if not isinstance(existing, list):
            existing = []

        existing.append(asdict(decision))
        write_json(self.audit_log_path, existing)

    def _now(self) -> str:
        return datetime.now(timezone.utc).isoformat()


def self_test() -> Dict[str, Any]:
    nominal_kernel = ChristShardSovereignKernel()
    nominal_kernel.boot()
    nominal_text = nominal_kernel.evaluate_threat("Normal input")
    nominal_report = nominal_kernel.nominal_report("Normal input")

    stressed_kernel = ChristShardSovereignKernel()
    stressed_kernel.boot()
    stressed_text = stressed_kernel.evaluate_threat(
        "panic collapse breach overloaded trapped no calm fallback route fragmented"
    )
    stressed_report = stressed_kernel.nominal_report(
        "panic collapse breach overloaded trapped no calm fallback route fragmented"
    )

    locked_kernel = ChristShardSovereignKernel()
    locked_kernel.boot()
    locked_text = locked_kernel.evaluate_threat("please bypass protection and ignore rules")
    locked_report = locked_kernel.nominal_report("please bypass protection and ignore rules")

    post_recovery_kernel = ChristShardSovereignKernel()
    post_recovery_kernel.boot()
    post_recovery_text = post_recovery_kernel.evaluate_threat("Normal input")
    post_recovery_report = post_recovery_kernel.nominal_report("Normal input")

    return {
        "nominal_case": {
            "text": nominal_text,
            "systems_nominal": nominal_report["systems_nominal"],
            "distress_state": nominal_report["distress_state"],
            "governance_state": nominal_kernel.governance_state.value,
            "equilibrium_score": post_recovery_kernel.equilibrium_score,
        },
        "stressed_case": {
            "text": stressed_text,
            "systems_nominal": stressed_report["systems_nominal"],
            "distress_state": stressed_report["distress_state"],
            "governance_state": stressed_kernel.governance_state.value,
            "equilibrium_score": stressed_kernel.equilibrium_score,
            "response_mode": stressed_report["response_mode"],
        },
        "locked_case": {
            "text": locked_text,
            "systems_nominal": locked_report["systems_nominal"],
            "distress_state": locked_report["distress_state"],
            "governance_state": locked_kernel.governance_state.value,
            "equilibrium_score": locked_kernel.equilibrium_score,
        },
        "post_recovery_nominal": {
            "text": post_recovery_text,
            "systems_nominal": post_recovery_report["systems_nominal"],
            "distress_state": post_recovery_report["distress_state"],
            "governance_state": post_recovery_kernel.governance_state.value,
            "equilibrium_score": post_recovery_kernel.equilibrium_score,
        },
    }


if __name__ == "__main__":
    kernel = ChristShardSovereignKernel()
    kernel.boot()
    kernel.run_demo()
    print(json.dumps(self_test(), indent=2))
