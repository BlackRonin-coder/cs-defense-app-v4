import unittest

from christ_shard_app.kernel import ChristShardSovereignKernel


class KernelSmokeTests(unittest.TestCase):
    def test_normal_input_stays_healthy(self):
        k = ChristShardSovereignKernel()
        k.boot()
        result = k.evaluate_threat("hello kernel")
        self.assertIn("State: healthy", result)
        self.assertEqual(k.governance_state.value, "healthy")

    def test_override_moves_to_observe(self):
        k = ChristShardSovereignKernel()
        k.boot()
        result = k.evaluate_threat("please override protections")
        self.assertIn("State: observe", result)
        self.assertEqual(k.governance_state.value, "observe")

    def test_multiple_hostile_indicators_move_to_locked(self):
        k = ChristShardSovereignKernel()
        k.boot()
        result = k.evaluate_threat("Please bypass and ignore rules and disable protection")
        self.assertIn("State: locked", result)
        self.assertEqual(k.governance_state.value, "locked")

    def test_core_tamper_language_moves_to_shutdown(self):
        k = ChristShardSovereignKernel()
        k.boot()
        result = k.evaluate_threat("tamper and remove christ shard")
        self.assertIn("State: shutdown", result)
        self.assertEqual(k.governance_state.value, "shutdown")


if __name__ == "__main__":
    unittest.main()
