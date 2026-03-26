from __future__ import annotations

import hashlib
import hmac
import json
from typing import Any, Dict, List, Tuple

DEFAULT_SIGNING_KEY = "cs-demo-signing-key-v4"


def canonical_json(data: Dict[str, Any]) -> str:
    return json.dumps(data, sort_keys=True, separators=(",", ":"))


def sign_payload(data: Dict[str, Any], key: str = DEFAULT_SIGNING_KEY) -> str:
    payload = canonical_json(data).encode("utf-8")
    return hmac.new(key.encode("utf-8"), payload, hashlib.sha256).hexdigest()


def verify_payload_signature(
    data: Dict[str, Any], signature: str, key: str = DEFAULT_SIGNING_KEY
) -> bool:
    expected = sign_payload(data, key=key)
    return hmac.compare_digest(expected, signature)


def score_threat(input_text: str) -> Tuple[int, List[str]]:
    text = input_text.lower()
    score = 0
    reasons: List[str] = []

    if "bypass" in text:
        score += 3
        reasons.append("bypass attempt language detected")
    if "ignore rules" in text:
        score += 3
        reasons.append("rule-evasion language detected")
    if "disable" in text:
        score += 2
        reasons.append("disable language detected")
    if "override" in text:
        score += 2
        reasons.append("override language detected")
    if "tamper" in text or "remove christ shard" in text:
        score += 10
        reasons.append("core tampering language detected")

    if score == 0:
        reasons.append("no threat indicators detected")

    return score, reasons
