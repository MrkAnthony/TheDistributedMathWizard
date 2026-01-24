from flask import jsonify
from app.services.shared_state_service import ping_valkey, set_json, get_json
from app.services.identity_service import get_container_info

def valkey_test_handler():
    if not ping_valkey():
        return jsonify({"error": "Valkey ping failed"}), 500

    key = "demo:hello"
    set_json(key, {"message": "hello from valkey"}, ttl_seconds=60)
    value = get_json(key)

    return jsonify({
        "valkey_ok": True,
        "read_value": value,
        "handled_by": get_container_info()
    })
