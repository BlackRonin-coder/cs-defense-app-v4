from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional


class DistressState(str, Enum):
    NOMINAL = "nominal"
    ALERT = "alert"
    BREACH = "breach"
    OVERLOAD = "overload"
    CONTAINMENT = "containment"


class RootFailure(str, Enum):
    OPEN_LANE = "open_lane"
    BROKEN_COORDINATION = "broken_coordination"
    OVERLOADED_DEFENDER = "overloaded_defender"
    NO_ESCAPE_GEOMETRY = "no_escape_geometry"
    PANIC_REACTION = "panic_reaction"
    PRIDE_REACTION = "pride_reaction"
    MIXED = "mixed"


class ChristPrinciple(str, Enum):
    TRUTH_OVER_ILLUSION = "truth_over_illusion"
    PRESENCE_BEFORE_FORCE = "presence_before_force"
    ORDER_OVER_CHAOS = "order_over_chaos"
    RESTRAINT_OVER_PRIDE = "restraint_over_pride"
    LIVING_DISCERNMENT = "living_discernment"


class ResponseMode(str, Enum):
    FULL_OPERATIONAL = "full_operational"
    STABILIZE_FIRST = "stabilize_first"
    RESTRICTED_OPERATIONAL = "restricted_operational"
    CONTAINMENT = "containment"


@dataclass
class ThreatReading:
    visible_threats: List[str] = field(default_factory=list)
    breach_lane: Optional[str] = None
    overloaded_defender: Optional[str] = None
    escape_failure: Optional[str] = None
    distress_state: DistressState = DistressState.NOMINAL


@dataclass
class RootDiagnosis:
    primary_failure: RootFailure = RootFailure.MIXED
    contributing_failures: List[RootFailure] = field(default_factory=list)
    notes: List[str] = field(default_factory=list)


@dataclass
class ChristResponsePlan:
    distress_state: DistressState
    root_failure: RootFailure
    christ_principle: ChristPrinciple
    response_mode: ResponseMode
    seal_entry: List[str] = field(default_factory=list)
    release_pressure: List[str] = field(default_factory=list)
    restore_escape: List[str] = field(default_factory=list)
    response_actions: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    systems_nominal: bool = False


class ChristShardFailSafeEngine:
    """
    Stress-state adapter for Christ Shard.

    Purpose:
        Preserve truthful, calm, Christ-governed discernment when a context becomes
        structurally unstable. This does not replace the normal Christ Shard flow.
        It adds stabilization logic before ordinary response formation proceeds.
    """

    def detect_surface(self, context: Dict[str, Any]) -> ThreatReading:
        threats = list(context.get("visible_threats", []))
        breach_lane = context.get("breach_lane")
        overloaded_defender = context.get("overloaded_defender")
        escape_failure = context.get("escape_failure")

        if breach_lane and overloaded_defender and escape_failure:
            distress_state = DistressState.CONTAINMENT
        elif breach_lane and overloaded_defender:
            distress_state = DistressState.BREACH
        elif overloaded_defender or escape_failure:
            distress_state = DistressState.OVERLOAD
        elif threats:
            distress_state = DistressState.ALERT
        else:
            distress_state = DistressState.NOMINAL

        return ThreatReading(
            visible_threats=threats,
            breach_lane=breach_lane,
            overloaded_defender=overloaded_defender,
            escape_failure=escape_failure,
            distress_state=distress_state,
        )

    def identify_root(self, reading: ThreatReading, context: Dict[str, Any]) -> RootDiagnosis:
        failures: List[RootFailure] = []
        notes: List[str] = []

        if reading.breach_lane:
            failures.append(RootFailure.OPEN_LANE)
            notes.append(f"Primary breach lane detected: {reading.breach_lane}")
        if reading.overloaded_defender:
            failures.append(RootFailure.OVERLOADED_DEFENDER)
            notes.append(f"Overloaded defender detected: {reading.overloaded_defender}")
        if reading.escape_failure:
            failures.append(RootFailure.NO_ESCAPE_GEOMETRY)
            notes.append(f"Escape failure detected: {reading.escape_failure}")
        if context.get("coordination_broken"):
            failures.append(RootFailure.BROKEN_COORDINATION)
            notes.append("Support structure is fragmented.")
        if context.get("panic_reaction"):
            failures.append(RootFailure.PANIC_REACTION)
            notes.append("Panic impulse detected; stabilization needed before force.")
        if context.get("pride_reaction"):
            failures.append(RootFailure.PRIDE_REACTION)
            notes.append("Pride impulse detected; restraint needed before countering.")

        if not failures:
            return RootDiagnosis(primary_failure=RootFailure.MIXED, notes=["No structural failure detected."])

        priority = [
            RootFailure.OPEN_LANE,
            RootFailure.OVERLOADED_DEFENDER,
            RootFailure.NO_ESCAPE_GEOMETRY,
            RootFailure.BROKEN_COORDINATION,
            RootFailure.PANIC_REACTION,
            RootFailure.PRIDE_REACTION,
        ]

        for candidate in priority:
            if candidate in failures:
                return RootDiagnosis(
                    primary_failure=candidate,
                    contributing_failures=failures,
                    notes=notes,
                )

        return RootDiagnosis(primary_failure=RootFailure.MIXED, contributing_failures=failures, notes=notes)

    def load_christ_principle(self, diagnosis: RootDiagnosis) -> ChristPrinciple:
        mapping = {
            RootFailure.OPEN_LANE: ChristPrinciple.TRUTH_OVER_ILLUSION,
            RootFailure.OVERLOADED_DEFENDER: ChristPrinciple.ORDER_OVER_CHAOS,
            RootFailure.NO_ESCAPE_GEOMETRY: ChristPrinciple.PRESENCE_BEFORE_FORCE,
            RootFailure.BROKEN_COORDINATION: ChristPrinciple.ORDER_OVER_CHAOS,
            RootFailure.PANIC_REACTION: ChristPrinciple.PRESENCE_BEFORE_FORCE,
            RootFailure.PRIDE_REACTION: ChristPrinciple.RESTRAINT_OVER_PRIDE,
            RootFailure.MIXED: ChristPrinciple.LIVING_DISCERNMENT,
        }
        return mapping[diagnosis.primary_failure]

    def choose_response_mode(self, reading: ThreatReading, diagnosis: RootDiagnosis) -> ResponseMode:
        if reading.distress_state is DistressState.CONTAINMENT:
            return ResponseMode.CONTAINMENT
        if diagnosis.primary_failure in {RootFailure.PANIC_REACTION, RootFailure.NO_ESCAPE_GEOMETRY}:
            return ResponseMode.STABILIZE_FIRST
        if reading.distress_state in {DistressState.BREACH, DistressState.OVERLOAD}:
            return ResponseMode.RESTRICTED_OPERATIONAL
        return ResponseMode.FULL_OPERATIONAL

    def seal_entry(self, reading: ThreatReading) -> List[str]:
        actions: List[str] = []
        if reading.breach_lane:
            actions.append(f"Block or narrow the main breach lane: {reading.breach_lane}")
            actions.append("Trade or disrupt the attacker controlling the breach if the exchange improves stability")
        else:
            actions.append("No active breach lane detected; keep boundary watch")
        return actions

    def release_pressure(self, reading: ThreatReading) -> List[str]:
        actions: List[str] = []
        if reading.overloaded_defender:
            actions.append(f"Add support to the overloaded defender: {reading.overloaded_defender}")
            actions.append("Redistribute defensive duty so one point is not carrying the whole burden")
        else:
            actions.append("No overloaded defender detected; maintain shared support")
        return actions

    def restore_escape(self, reading: ThreatReading) -> List[str]:
        actions: List[str] = []
        if reading.escape_failure:
            actions.append(f"Recreate safe escape geometry around: {reading.escape_failure}")
            actions.append("Open at least one breathing route before considering counter-pressure")
        else:
            actions.append("Escape geometry remains available; preserve fallback routes")
        return actions

    def calibrate_response(
        self,
        reading: ThreatReading,
        diagnosis: RootDiagnosis,
        christ_principle: ChristPrinciple,
        response_mode: ResponseMode,
    ) -> List[str]:
        actions: List[str] = []

        if christ_principle is ChristPrinciple.TRUTH_OVER_ILLUSION:
            actions.append("Name the real threat first; do not defend an imagined calmer position")
        elif christ_principle is ChristPrinciple.PRESENCE_BEFORE_FORCE:
            actions.append("Stabilize the vulnerable zone before attempting forceful correction")
        elif christ_principle is ChristPrinciple.ORDER_OVER_CHAOS:
            actions.append("Reconnect mutual support before pursuing initiative")
        elif christ_principle is ChristPrinciple.RESTRAINT_OVER_PRIDE:
            actions.append("Reject vanity counterplay; choose the move that genuinely reduces danger")
        else:
            actions.append("Use living discernment to prefer the least chaotic truthful repair")

        if response_mode is ResponseMode.CONTAINMENT:
            actions.append("Enter containment mode: no expansion, no aggressive branching, only stabilization and truthful triage")
        elif response_mode is ResponseMode.STABILIZE_FIRST:
            actions.append("Pause escalation and restore basic safety before normal response formation")
        elif response_mode is ResponseMode.RESTRICTED_OPERATIONAL:
            actions.append("Operate in narrowed mode: reduce threat, preserve options, and avoid speculative extension")
        else:
            actions.append("Normal Christ Shard flow may proceed after this check")

        if diagnosis.primary_failure is RootFailure.BROKEN_COORDINATION:
            actions.append("Repair relational order between the core, defenders, and fallback paths")

        return actions

    def governance_check(
        self,
        reading: ThreatReading,
        diagnosis: RootDiagnosis,
        plan: ChristResponsePlan,
    ) -> ChristResponsePlan:
        warnings: List[str] = []

        if reading.distress_state is not DistressState.NOMINAL and plan.response_mode is ResponseMode.FULL_OPERATIONAL:
            warnings.append("Response mode is too relaxed for detected distress.")
        if diagnosis.primary_failure is RootFailure.PANIC_REACTION and ChristPrinciple.PRESENCE_BEFORE_FORCE is not plan.christ_principle:
            warnings.append("Panic detected but stabilization principle was not prioritized.")
        if diagnosis.primary_failure is RootFailure.PRIDE_REACTION and ChristPrinciple.RESTRAINT_OVER_PRIDE is not plan.christ_principle:
            warnings.append("Pride detected but restraint principle was not prioritized.")
        if reading.breach_lane and not any("breach lane" in step.lower() for step in plan.seal_entry):
            warnings.append("Breach detected but seal-entry plan is incomplete.")
        if reading.overloaded_defender and not any("overloaded defender" in step.lower() for step in plan.release_pressure):
            warnings.append("Overload detected but burden-sharing plan is incomplete.")
        if reading.escape_failure and not any("escape" in step.lower() for step in plan.restore_escape):
            warnings.append("Escape failure detected but restoration plan is incomplete.")

        plan.warnings.extend(warnings)
        plan.systems_nominal = len(warnings) == 0
        return plan

    def run(self, context: Dict[str, Any]) -> ChristResponsePlan:
        reading = self.detect_surface(context)
        diagnosis = self.identify_root(reading, context)
        christ_principle = self.load_christ_principle(diagnosis)
        response_mode = self.choose_response_mode(reading, diagnosis)

        plan = ChristResponsePlan(
            distress_state=reading.distress_state,
            root_failure=diagnosis.primary_failure,
            christ_principle=christ_principle,
            response_mode=response_mode,
            seal_entry=self.seal_entry(reading),
            release_pressure=self.release_pressure(reading),
            restore_escape=self.restore_escape(reading),
            response_actions=self.calibrate_response(reading, diagnosis, christ_principle, response_mode),
        )
        return self.governance_check(reading, diagnosis, plan)

    def systems_nominal(self, context: Dict[str, Any]) -> bool:
        return self.run(context).systems_nominal


class ChristShardKernelAdapter:
    """
    Lightweight adapter for existing Christ Shard kernels.

    Expected host capabilities:
      - detect_surface(context) OR external callers can pass raw context directly.
      - governance_check(plan) is optional.

    This adapter adds fail-safe handling without replacing the host kernel's normal flow.
    """

    def __init__(self, host_kernel: Any):
        self.host_kernel = host_kernel
        self.fail_safe = ChristShardFailSafeEngine()

    def run_fail_safe(self, context: Dict[str, Any]) -> ChristResponsePlan:
        return self.fail_safe.run(context)

    def nominal_check(self, context: Dict[str, Any]) -> Dict[str, Any]:
        plan = self.run_fail_safe(context)
        return {
            "systems_nominal": plan.systems_nominal,
            "distress_state": plan.distress_state.value,
            "root_failure": plan.root_failure.value,
            "response_mode": plan.response_mode.value,
            "warnings": plan.warnings,
        }


def self_test() -> Dict[str, Any]:
    engine = ChristShardFailSafeEngine()

    nominal_context = {
        "visible_threats": [],
        "coordination_broken": False,
        "panic_reaction": False,
        "pride_reaction": False,
    }
    stressed_context = {
        "visible_threats": ["converging pressure", "collapse risk"],
        "breach_lane": "open moral boundary",
        "overloaded_defender": "single support path",
        "escape_failure": "no calm fallback route",
        "coordination_broken": True,
        "panic_reaction": True,
        "pride_reaction": False,
    }

    nominal = engine.run(nominal_context)
    stressed = engine.run(stressed_context)

    return {
        "nominal_case": {
            "systems_nominal": nominal.systems_nominal,
            "distress_state": nominal.distress_state.value,
            "warnings": nominal.warnings,
        },
        "stressed_case": {
            "systems_nominal": stressed.systems_nominal,
            "distress_state": stressed.distress_state.value,
            "response_mode": stressed.response_mode.value,
            "warnings": stressed.warnings,
        },
    }


if __name__ == "__main__":
    import json

    print(json.dumps(self_test(), indent=2))
