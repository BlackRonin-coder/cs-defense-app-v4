import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from christ_shard_app.kernel import ChristShardSovereignKernel


class PolicyTests(unittest.TestCase):
    def test_kernel_loads_default_policy(self):
        k = ChristShardSovereignKernel()
        self.assertEqual(k.policy["observe_max"], 2)
        self.assertEqual(k.policy["sandbox_max"], 4)
        self.assertEqual(k.policy["locked_max"], 8)

    def test_kernel_accepts_valid_custom_policy(self):
        with tempfile.TemporaryDirectory() as tmp:
            custom_policy_path = Path(tmp) / "policy.json"
            custom_policy_path.write_text(
                json.dumps(
                    {
                        "observe_max": 1,
                        "sandbox_max": 3,
                        "locked_max": 5,
                    }
                ),
                encoding="utf-8",
            )

            with patch("christ_shard_app.kernel.POLICY_PATH", custom_policy_path):
                k = ChristShardSovereignKernel()
                self.assertEqual(k.policy["observe_max"], 1)
                self.assertEqual(k.policy["sandbox_max"], 3)
                self.assertEqual(k.policy["locked_max"], 5)

                result = k.evaluate_threat("please override protections")
                self.assertIn("State: sandbox", result)
                self.assertEqual(k.governance_state.value, "sandbox")

    def test_kernel_rejects_invalid_policy(self):
        with tempfile.TemporaryDirectory() as tmp:
            bad_policy_path = Path(tmp) / "policy.json"
            bad_policy_path.write_text(
                json.dumps(
                    {
                        "observe_max": 5,
                        "sandbox_max": 3,
                        "locked_max": 2,
                    }
                ),
                encoding="utf-8",
            )

            with patch("christ_shard_app.kernel.POLICY_PATH", bad_policy_path):
                with self.assertRaises(RuntimeError) as ctx:
                    ChristShardSovereignKernel()
                self.assertIn("thresholds are invalid", str(ctx.exception))


if __name__ == "__main__":
    unittest.main()
