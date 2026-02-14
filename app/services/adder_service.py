import time
from app.services.exceptions import MathWizardError

def add_two_items(a, b):
    # 1. Validation (Fast)
    if a is None or b is None:
        raise MathWizardError("Missing params: a and b are required.", 400)

    # 2. The "Real" Work (CPU Bound)
    # Instead of sleeping, we force the CPU to do math for 15 seconds.
    # This will spike your Docker Container CPU usage to 100%.
    duration = 2
    end_time = time.time() + duration
    
    while time.time() < end_time:
        # Perform a trivial calculation to keep the CPU core busy
        _ = a * b 

    # 3. Return Result
    return a + b