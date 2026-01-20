from flask import request, jsonify
from app.services.adder_service import add_two_items
from app.services.identity_service import get_container_info

def add_handler():
    a = request.args.get('a', type=float)
    b = request.args.get('b', type=float)
    
    if a is None or b is None:
        return jsonify({"error": "Missing params"}), 400
        
    calc_res = add_two_items(a, b)
    identity = get_container_info()

    res_data = {
        "handled_by": identity,
        "sum": calc_res
    }

    return jsonify(res_data)