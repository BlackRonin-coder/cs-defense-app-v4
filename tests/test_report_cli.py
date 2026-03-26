import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


class ReportCLITests(unittest.TestCase):
    def test_report_command_writes_health_report_json(self):
        with tempfile.TemporaryDirectory() as tmp:
            old_cwd = os.getcwd()
            try:
                os.chdir(tmp)
                state_dir = Path("state")
                state_dir.mkdir(exist_ok=True)

                (state_dir / "last_decision.json").write_text(
                    json.dumps(
                        {
                            "input_text": "hello kernel",
                            "reasons": ["no threat indicators detected"],
                            "score": 0,
                            "state": "healthy",
                            "timestamp": "2026-03-26T00:00:00+00:00",
                        }
                    ),
                    encoding="utf-8",
                )

                repo_root = Path(old_cwd)
                report_path = Path("state/custom_health_report.json")

                result = subprocess.run(
                    [
                        sys.executable,
                        str(repo_root / "cli.py"),
                        "report",
                        "--path",
                        str(report_path),
                    ],
                    capture_output=True,
                    text=True,
                    check=True,
                )

                self.assertIn("=== Health Report Exported ===", result.stdout)
                self.assertTrue(report_path.exists())

                payload = json.loads(report_path.read_text(encoding="utf-8"))
                self.assertTrue(payload["integrity_verified"])
                self.assertIn("active_policy", payload)
                self.assertIn("state_files", payload)
                self.assertIn("last_saved_decision", payload)
                self.assertEqual(payload["last_saved_decision"]["state"], "healthy")
            finally:
                os.chdir(old_cwd)


if __name__ == "__main__":
    unittest.main()
