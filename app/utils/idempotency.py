import hashlib
import json

def generate_request_hash(payload: dict) -> str:
    normalized = json.dumps(
        payload,
        sort_keys=True,
        separators=(",", ":"),
        default=str)
    return hashlib.sha256(normalized.encode("utf-8")).hexdigest()