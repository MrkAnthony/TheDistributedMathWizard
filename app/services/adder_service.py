from app.services.exceptions import MathWizardError
import time


def add_two_items(a, b):
    time.sleep(15)  # Simulate 15 seconds of work
    if a is None or b is None:
        raise MathWizardError("Missing params: a and b are required.", 400)

    return a + b
