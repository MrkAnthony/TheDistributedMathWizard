from flask import jsonify
from app.services.identity_service import get_container_info

def identity_handler():

    res_data = get_container_info()
    
    return jsonify(res_data)