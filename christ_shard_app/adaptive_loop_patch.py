
# === REPEAT ATTACK BOOST ===
def boost_repeat_attacker(profile, result):
    if profile["attempts"] > 1:
        result["repeat_attacker"] = True
        result["defence_mode"] = "preemptive_restriction"
        print("[REPEAT ATTACK DETECTED] Escalating immediately")
    return result

# extend apply logic
_original_apply = apply_adaptive_logic

def enhanced_apply(event, result):
    result = _original_apply(event, result)
    profile = profiler.update_profile(
        event.actor_id,
        event.behaviours,
        event.touched_subsystems
    )
    result = boost_repeat_attacker(profile, result)
    return result

apply_adaptive_logic = enhanced_apply

# === DECEPTION ENGINE PATCH ===
from christ_shard_app.deception_engine import DeceptionEngine

deception_engine = DeceptionEngine()

def apply_deception(profile, result):
    env = deception_engine.generate_environment(profile)
    result["deception_environment"] = env

    print("[DECEPTION ENVIRONMENT]", env)
    return result

# extend adaptive logic with deception
_old_apply = apply_adaptive_logic

def full_adaptive(event, result):
    result = _old_apply(event, result)

    profile = profiler.update_profile(
        event.actor_id,
        event.behaviours,
        event.touched_subsystems
    )

    result = apply_deception(profile, result)
    return result

apply_adaptive_logic = full_adaptive

# === TARGETED DECEPTION INTEGRATION ===
def apply_targeted_deception(profile, result):
    trap = deception_engine.generate_targeted_trap(profile)
    result["targeted_deception"] = trap

    print("[TARGETED TRAP]", trap)
    return result

# extend again
_prev_apply = apply_adaptive_logic

def final_adaptive(event, result):
    result = _prev_apply(event, result)

    profile = profiler.update_profile(
        event.actor_id,
        event.behaviours,
        event.touched_subsystems
    )

    result = apply_targeted_deception(profile, result)
    return result

apply_adaptive_logic = final_adaptive

# === EVOLVING DECEPTION INTEGRATION ===
def apply_evolving_deception(profile, event, result):
    trap = deception_engine.generate_targeted_trap(profile)
    trap = deception_engine.evolve_trap(trap, event.behaviours)

    result["evolving_trap"] = trap

    print("[EVOLVING TRAP]", trap)
    return result

# extend final layer
_prev = apply_adaptive_logic

def ultimate_adaptive(event, result):
    result = _prev(event, result)

    profile = profiler.update_profile(
        event.actor_id,
        event.behaviours,
        event.touched_subsystems
    )

    result = apply_evolving_deception(profile, event, result)
    return result

apply_adaptive_logic = ultimate_adaptive

# === PREDICTION INTEGRATION ===
from christ_shard_app.prediction_engine import predict_next_move

def apply_prediction(profile, result):
    prediction = predict_next_move(profile)

    result["prediction"] = prediction

    print("[PREDICTION]", prediction)
    return result

# extend system again
_prev_layer = apply_adaptive_logic

def supreme_adaptive(event, result):
    result = _prev_layer(event, result)

    profile = profiler.update_profile(
        event.actor_id,
        event.behaviours,
        event.touched_subsystems
    )

    result = apply_prediction(profile, result)
    return result

apply_adaptive_logic = supreme_adaptive

# === PATTERN INTELLIGENCE INTEGRATION ===
from christ_shard_app.pattern_engine import update_sequence, detect_pattern, predict_from_pattern

def apply_pattern_intelligence(event, result):
    seq = update_sequence(event.actor_id, event.behaviours[0])
    pattern = detect_pattern(seq)
    next_step = predict_from_pattern(pattern)

    result["pattern"] = pattern
    result["pattern_prediction"] = next_step

    print("[PATTERN]", pattern)
    print("[PATTERN NEXT]", next_step)

    return result

_prev_final = apply_adaptive_logic

def apex_adaptive(event, result):
    result = _prev_final(event, result)
    result = apply_pattern_intelligence(event, result)
    return result

apply_adaptive_logic = apex_adaptive

# === SELF-LEARNING PATTERN PATCH ===
from christ_shard_app.pattern_engine import learn_pattern

def apply_self_learning_pattern(event, result):
    seq = update_sequence(event.actor_id, event.behaviours[0])
    learned = learn_pattern(event.actor_id, seq)

    result["learned_pattern"] = learned

    print("[LEARNED PATTERN]", learned)
    return result

_previous_apex = apply_adaptive_logic

def ultimate_pattern_adaptive(event, result):
    result = _previous_apex(event, result)
    result = apply_self_learning_pattern(event, result)
    return result

apply_adaptive_logic = ultimate_pattern_adaptive

# === FORCE FINAL EXECUTION LAYER ===
def final_system_layer(event, result):
    profile = profiler.update_profile(
        event.actor_id,
        event.behaviours,
        event.touched_subsystems
    )

    # run ALL systems explicitly
    result = apply_prediction(profile, result)
    result = apply_pattern_intelligence(event, result)
    result = apply_self_learning_pattern(event, result)

    return result

apply_adaptive_logic = final_system_layer
