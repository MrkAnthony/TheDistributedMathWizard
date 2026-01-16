import docker
import logging


# This retrieves the containers info {id, name}
def get_container_info():
    client = docker.from_env()
    all_containers = client.containers.list()
    container = all_containers[0]
    try:
        cont_id = container.id
        cont_name = container.name
        data = {"id": cont_id, "name": cont_name}
        return data
    except docker.errors.APIError as e:
        logging.error(f"failed to retrieve: {e}")
