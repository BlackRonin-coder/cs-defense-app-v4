
# === PATTERN MEMORY ===
attack_sequences = {}

def update_sequence(actor_id, behaviour):
    if actor_id not in attack_sequences:
        attack_sequences[actor_id] = []

    attack_sequences[actor_id].append(behaviour)

    # keep last 5 actions only (bounded memory)
    attack_sequences[actor_id] = attack_sequences[actor_id][-5:]

    return attack_sequences[actor_id]

# === PATTERN DETECTION ===
def detect_pattern(sequence):
    patterns = {
        ("probe_input", "inject_unverified_code"): "intrusion_chain",
        ("inject_unverified_code", "modify_governance"): "escalation_chain",
        ("modify_governance", "exfiltrate_memory"): "takeover_chain"
    }

    for pattern, label in patterns.items():
        if tuple(sequence[-len(pattern):]) == pattern:
            return label

    return "unknown"

# === PATTERN-BASED PREDICTION ===
def predict_from_pattern(pattern):
    mapping = {
        "intrusion_chain": "modify_governance",
        "escalation_chain": "exfiltrate_memory",
        "takeover_chain": "full_compromise"
    }

    return mapping.get(pattern, None)

# === SELF-LEARNING PATTERN DISCOVERY ===
observed_patterns = {}

def learn_pattern(actor_id, sequence):
    if len(sequence) < 2:
        return None

    pair = tuple(sequence[-2:])

    if actor_id not in observed_patterns:
        observed_patterns[actor_id] = {}

    observed_patterns[actor_id][pair] = observed_patterns[actor_id].get(pair, 0) + 1
    return {"pair": pair, "count": observed_patterns[actor_id][pair]}
