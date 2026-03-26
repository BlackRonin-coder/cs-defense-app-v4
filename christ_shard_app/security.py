from __future__ import annotations
import hashlib, hmac, json
from pathlib import Path
from typing import Any, Dict

DEFAULT_SIGNING_KEY = "cs-demo-signing-key-v4"

def canonical_json(data: Dict[str, Any]) -> str:
    return json.dumps(data, sort_keys=True, separators=(",", ":"))

def sign_payload(data: Dict[str, Any], key: str = DEFAULT_SIGNING_KEY) -> str:
    payload = canonical_json(data).encode("utf-8")
    return hmac.new(key.encode("utf-8"), payload, hashlib.sha256).hexdigest()

def verify_payload_signature(data: Dict[str, Any], signature: str, key: str = DEFAULT_SIGNING_KEY) -> bool:
    expected = sign_payload(data, key=key)
    return hmac.compare_digest(expected, signature)
