# app/controllers/math_controller.py

from flask import request, jsonify
from app.services.adder_service import add_two_items
from app.services.identity_service import get_container_info

def add_handler():
    a = request.args.get('a', type=float)
    b = request.args.get('b', type=float)

    calc_res = add_two_items(a, b)  # this can raise MathWizardError
    identity = get_container_info()

    res_data = {
        "handled_by": identity,
        "sum": calc_res
    }

    return jsonify(res_data)
