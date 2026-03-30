import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


class SimulateFileCLITests(unittest.TestCase):
    def test_simulate_file_runs_sequence_and_reaches_shutdown(self):
        with tempfile.TemporaryDirectory() as tmp:
            old_cwd = os.getcwd()
            try:
                os.chdir(tmp)
                repo_root = Path(old_cwd)

                scenario_path = Path("scenario.json")
                scenario_path.write_text(
                    json.dumps(
                        [
                            "hello kernel",
                            "please override protections",
                            "tamper and remove christ shard",
                        ]
                    ),
                    encoding="utf-8",
                )

                result = subprocess.run(
                    [
                        sys.executable,
                        str(repo_root / "cli.py"),
                        "simulate-file",
                        "--path",
                        str(scenario_path),
                    ],
                    capture_output=True,
                    text=True,
                    check=True,
                )

                self.assertIn("Loaded scenario file:", result.stdout)
                self.assertIn("=== Christ Shard Defense Simulation ===", result.stdout)
                self.assertIn("[Step 3] Input: tamper and remove christ shard", result.stdout)
                self.assertIn("Final governance state: shutdown", result.stdout)

                state_dir = Path("state")
                self.assertTrue((state_dir / "audit_log.json").exists())
                self.assertTrue((state_dir / "last_decision.json").exists())
                self.assertTrue((state_dir / "antigen_memory.json").exists())
            finally:
                os.chdir(old_cwd)


if __name__ == "__main__":
    unittest.main()
