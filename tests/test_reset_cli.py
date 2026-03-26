import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


class ResetCLITests(unittest.TestCase):
    def test_reset_requires_explicit_yes_flag(self):
        with tempfile.TemporaryDirectory() as tmp:
            old_cwd = os.getcwd()
            try:
                os.chdir(tmp)
                state_dir = Path("state")
                state_dir.mkdir(exist_ok=True)
                for name in ["audit_log.json", "last_decision.json", "antigen_memory.json"]:
                    (state_dir / name).write_text(json.dumps({"present": True}), encoding="utf-8")

                repo_root = Path(old_cwd)
                result = subprocess.run(
                    [sys.executable, str(repo_root / "cli.py"), "reset"],
                    capture_output=True,
                    text=True,
                    check=True,
                )

                self.assertIn("Reset aborted", result.stdout)
                self.assertTrue((state_dir / "audit_log.json").exists())
                self.assertTrue((state_dir / "last_decision.json").exists())
                self.assertTrue((state_dir / "antigen_memory.json").exists())
            finally:
                os.chdir(old_cwd)

    def test_reset_yes_removes_runtime_state_files(self):
        with tempfile.TemporaryDirectory() as tmp:
            old_cwd = os.getcwd()
            try:
                os.chdir(tmp)
                state_dir = Path("state")
                state_dir.mkdir(exist_ok=True)
                for name in ["audit_log.json", "last_decision.json", "antigen_memory.json"]:
                    (state_dir / name).write_text(json.dumps({"present": True}), encoding="utf-8")

                repo_root = Path(old_cwd)
                result = subprocess.run(
                    [sys.executable, str(repo_root / "cli.py"), "reset", "--yes"],
                    capture_output=True,
                    text=True,
                    check=True,
                )

                self.assertIn("Runtime State Reset", result.stdout)
                self.assertFalse((state_dir / "audit_log.json").exists())
                self.assertFalse((state_dir / "last_decision.json").exists())
                self.assertFalse((state_dir / "antigen_memory.json").exists())
            finally:
                os.chdir(old_cwd)


if __name__ == "__main__":
    unittest.main()
