
# === PREDICTION ENGINE ===
def predict_next_move(profile):
    behaviours = profile.get("known_behaviours", [])

    prediction = {
        "likely_next": None,
        "confidence": "low"
    }

    if "probe_input" in behaviours:
        prediction["likely_next"] = "inject_unverified_code"
        prediction["confidence"] = "medium"

    if "inject_unverified_code" in behaviours:
        prediction["likely_next"] = "modify_governance"
        prediction["confidence"] = "high"

    if "modify_governance" in behaviours:
        prediction["likely_next"] = "exfiltrate_memory"
        prediction["confidence"] = "high"

    return prediction
