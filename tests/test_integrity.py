import os
import tempfile
import unittest
from unittest.mock import patch

from christ_shard_app.kernel import (
    ChristShard,
    ChristShardSovereignKernel,
    EXPECTED_SHARD_FINGERPRINT,
)


class IntegrityTests(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self._old_cwd = os.getcwd()
        os.chdir(self._tmp.name)

    def tearDown(self):
        os.chdir(self._old_cwd)
        self._tmp.cleanup()

    def test_manifest_fingerprint_matches_expected_constant(self):
        shard = ChristShard()
        self.assertEqual(shard.fingerprint(), EXPECTED_SHARD_FINGERPRINT)

    def test_boot_fails_if_expected_fingerprint_is_wrong(self):
        with patch("christ_shard_app.kernel.EXPECTED_SHARD_FINGERPRINT", "WRONG_FINGERPRINT"):
            kernel = ChristShardSovereignKernel()
            with self.assertRaises(RuntimeError) as ctx:
                kernel.boot()
            self.assertIn("fingerprint mismatch", str(ctx.exception))
            self.assertEqual(kernel.governance_state.value, "shutdown")


if __name__ == "__main__":
    unittest.main()
