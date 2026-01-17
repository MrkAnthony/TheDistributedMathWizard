import socket

def get_container_info():
    container_id = socket.gethostname()
    return {"id": container_id}
