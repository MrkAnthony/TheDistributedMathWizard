import os
import json
import redis

VALKEY_HOST = os.getenv("VALKEY_HOST", "valkey")
VALKEY_PORT = int(os.getenv("VALKEY_PORT", "6379"))

_client = redis.Redis(host=VALKEY_HOST, port=VALKEY_PORT, decode_responses=True)

def ping_valkey() -> bool:
    return _client.ping()

def set_json(key: str, value: dict, ttl_seconds: int | None = None) -> None:
    payload = json.dumps(value)
    if ttl_seconds is not None:
        _client.setex(key, ttl_seconds, payload)
    else:
        _client.set(key, payload)

def get_json(key: str) -> dict | None:
    raw = _client.get(key)
    if raw is None:
        return None
    return json.loads(raw)
