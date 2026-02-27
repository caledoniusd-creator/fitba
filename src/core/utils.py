from functools import wraps
from random import randint
from sys import maxsize
from time import perf_counter

import logging


def timer(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        start = perf_counter()
        result = func(*args, **kwargs)
        end = perf_counter()
        logging.getLogger().info(f"{func.__name__} took {end - start:.6f} seconds")
        return result

    return wrapper


def random_seed():
    return randint(0, maxsize)
