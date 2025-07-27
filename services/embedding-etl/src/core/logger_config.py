import logging
import sys
from functools import wraps
from inspect import iscoroutinefunction


def get_logger(name: str) -> logging.Logger:
    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG)

    if not logger.hasHandlers():
        formatter = logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        )

        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)
    return logger


logger = get_logger(__name__)


def log_call(func):
    if iscoroutinefunction(func):

        @wraps(func)
        async def wrapper(*args, **kwargs):
            logger.info(f"→ {func.__name__} args={args} kwargs={kwargs}")
            result = await func(*args, **kwargs)
            logger.info(f"← {func.__name__} returned={result!r}")
            return result

    else:

        @wraps(func)
        def wrapper(*args, **kwargs):
            logger.info(f"→ {func.__name__} args={args} kwargs={kwargs}")
            result = func(*args, **kwargs)
            logger.info(f"← {func.__name__} returned={result!r}")
            return result

    return wrapper
