import os
import redis

def get_redis_client() -> redis.Redis:
    host = os.getenv("VALKEY_HOST", "localhost")
    port = int(os.getenv("VALKEY_PORT", "6379"))

    # decode_responses=True makes get/set return strings (not bytes)
    return redis.Redis(host=host, port=port, decode_responses=True)
