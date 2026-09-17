import time
from collections.abc import Callable
from functools import wraps


def retry_with_backoff(
    retries: int = 3,
    initial_delay: float = 2.0,
    multiplier: float = 2.0,
):
    """
    Retry transient API failures using exponential backoff.
    """

    def decorator(func: Callable):
        @wraps(func)
        def wrapper(*args, **kwargs):
            delay = initial_delay

            for attempt in range(retries + 1):
                try:
                    return func(*args, **kwargs)

                except Exception:
                    if attempt == retries:
                        raise

                    time.sleep(delay)
                    delay *= multiplier

        return wrapper

    return decorator