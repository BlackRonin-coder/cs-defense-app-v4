import os
import tempfile
import unittest
from pathlib import Path

from christ_shard_app.kernel import ChristShardSovereignKernel
from christ_shard_app.storage import read_json, write_json


class StorageLayerTests(unittest.TestCase):
    def test_write_and_read_json_roundtrip(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "sample.json"
            payload = {"state": "healthy", "score": 0}
            write_json(path, payload)
            loaded = read_json(path, default={})
            self.assertEqual(loaded, payload)

    def test_read_json_returns_default_for_missing_file(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "missing.json"
            loaded = read_json(path, default={"fallback": True})
            self.assertEqual(loaded, {"fallback": True})

    def test_kernel_writes_persistent_state_files(self):
        with tempfile.TemporaryDirectory() as tmp:
            old_cwd = os.getcwd()
            try:
                os.chdir(tmp)
                k = ChristShardSovereignKernel()
                k.boot()
                k.evaluate_threat("please override protections")

                state_dir = Path("state")
                self.assertTrue((state_dir / "audit_log.json").exists())
                self.assertTrue((state_dir / "last_decision.json").exists())
                self.assertTrue((state_dir / "antigen_memory.json").exists())

                last_decision = read_json(state_dir / "last_decision.json", default={})
                antigen_memory = read_json(state_dir / "antigen_memory.json", default=[])

                self.assertEqual(last_decision.get("state"), "observe")
                self.assertIn("override language detected", antigen_memory)
            finally:
                os.chdir(old_cwd)


if __name__ == "__main__":
    unittest.main()
