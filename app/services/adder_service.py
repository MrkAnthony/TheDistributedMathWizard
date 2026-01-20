from app.services.exceptions import MathWizardError

def add_two_items(a, b):
    if a is None or b is None:
        raise MathWizardError("Missing params: a and b are required.", 400)

    return a + b