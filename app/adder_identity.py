import socket

def add_with_identity(a, b):
    result = a + b
    server_id = socket.gethostname()

    return {
        "sum": result,
        "handled_by": server_id
    }
