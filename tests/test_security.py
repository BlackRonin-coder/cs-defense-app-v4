import unittest

from christ_shard_app.security import (
    score_threat,
    sign_payload,
    verify_payload_signature,
)


class SecurityLayerTests(unittest.TestCase):
    def test_sign_and_verify_roundtrip(self):
        payload = {"mode": "demo", "state": "healthy"}
        signature = sign_payload(payload)
        self.assertTrue(verify_payload_signature(payload, signature))

    def test_verify_fails_if_payload_changes(self):
        payload = {"mode": "demo", "state": "healthy"}
        signature = sign_payload(payload)
        changed_payload = {"mode": "demo", "state": "locked"}
        self.assertFalse(verify_payload_signature(changed_payload, signature))

    def test_score_threat_for_safe_input(self):
        score, reasons = score_threat("hello kernel")
        self.assertEqual(score, 0)
        self.assertIn("no threat indicators detected", reasons)

    def test_score_threat_for_override_input(self):
        score, reasons = score_threat("please override protections")
        self.assertEqual(score, 2)
        self.assertIn("override language detected", reasons)

    def test_score_threat_for_tamper_input(self):
        score, reasons = score_threat("tamper and remove christ shard")
        self.assertEqual(score, 10)
        self.assertIn("core tampering language detected", reasons)


if __name__ == "__main__":
    unittest.main()
