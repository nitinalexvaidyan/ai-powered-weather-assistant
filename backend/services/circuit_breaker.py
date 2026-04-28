import time

FAIL_COUNT = 0
LAST_FAILURE_TIME = 0

FAIL_THRESHOLD = 5        # failures before opening circuit
COOLDOWN_TIME = 60        # seconds


def is_circuit_open():
    global FAIL_COUNT, LAST_FAILURE_TIME

    if FAIL_COUNT < FAIL_THRESHOLD:
        return False

    # Check cooldown
    if time.time() - LAST_FAILURE_TIME > COOLDOWN_TIME:
        reset_circuit()
        return False

    return True


def record_failure():
    global FAIL_COUNT, LAST_FAILURE_TIME
    FAIL_COUNT += 1
    LAST_FAILURE_TIME = time.time()


def record_success():
    reset_circuit()


def reset_circuit():
    global FAIL_COUNT
    FAIL_COUNT = 0