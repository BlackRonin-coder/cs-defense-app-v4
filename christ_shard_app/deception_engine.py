import random

class DeceptionEngine:

    def __init__(self):
        self.deception_profiles = {}

    def generate_environment(self, profile):
        risk = profile.get("risk_level", "low")

        if risk == "low":
            depth = "shallow"
        elif risk == "medium":
            depth = "interactive"
        elif risk == "high":
            depth = "complex"
        else:
            depth = "full_simulation"

        return {
            "illusion_depth": depth,
            "fake_vulnerabilities": self._generate_vulns(depth),
            "data_surface": self._generate_data(depth)
        }

    def _generate_vulns(self, depth):
        base = ["open_port", "weak_validation"]

        if depth in ["interactive", "complex", "full_simulation"]:
            base += ["fake_admin_panel", "dummy_api"]

        if depth in ["complex", "full_simulation"]:
            base += ["fake_database", "decoy_credentials"]

        if depth == "full_simulation":
            base += ["full_system_clone"]

        return base

    def _generate_data(self, depth):
        return {
            "files": random.randint(5, 50),
            "endpoints": random.randint(2, 20),
            "fake_users": random.randint(1, 10)
        }

# === TARGETED DECEPTION PATCH ===
def generate_targeted_trap(self, profile):
    behaviours = profile.get("known_behaviours", [])

    trap = {
        "illusion_depth": "adaptive",
        "bait": [],
        "narrative": ""
    }

    if "inject_unverified_code" in behaviours:
        trap["bait"].append("fake_code_execution_path")

    if "modify_governance" in behaviours:
        trap["bait"].append("fake_admin_controls")

    if "exfiltrate_memory" in behaviours:
        trap["bait"].append("fake_sensitive_data")

    if "probe_input" in behaviours:
        trap["bait"].append("fake_input_vectors")

    if "spam_inputs" in behaviours:
        trap["bait"].append("rate_limit_bypass_illusion")

    trap["narrative"] = "attacker appears to be progressing deeper into system"

    return trap

# attach method
DeceptionEngine.generate_targeted_trap = generate_targeted_trap

# === EVOLVING DECEPTION PATCH ===
def evolve_trap(self, trap, behaviours):
    if "inject_unverified_code" in behaviours:
        trap["illusion_depth"] = "deep_code_path"
        trap["narrative"] = "code execution appears successful"

    if "modify_governance" in behaviours:
        trap["illusion_depth"] = "admin_control"
        trap["narrative"] = "governance control appears gained"

    if "exfiltrate_memory" in behaviours:
        trap["illusion_depth"] = "data_extraction"
        trap["narrative"] = "sensitive data appears accessible"

    return trap

DeceptionEngine.evolve_trap = evolve_trap
