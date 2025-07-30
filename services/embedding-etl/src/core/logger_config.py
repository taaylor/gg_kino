import logging
import reprlib
import sys
from functools import wraps
from inspect import iscoroutinefunction
from typing import Any, Callable


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


reprer = reprlib.Repr()


def log_call(
    short_input: bool = False,
    short_output: bool = False,
    max_items_for_showing_in_log: int = 5,
):
    """
    Фабрика декоратора для логирования входных аргументов и результата функции.

    :param short_input: если True, обрезает длинные входные аргументы в логе.
    :param short_output: если True, обрезает длинный вывод в логе.
    :param max_items_for_showing_in_log: максимальное число элементов для ввода и вывода.

    :return: декоратор, добавляющий логирование начала, входа и выхода выполнения функции.
    """
    # подготовим repr-фабрику
    reprer.maxlist = max_items_for_showing_in_log  # списки
    reprer.maxdict = max_items_for_showing_in_log  # словари
    reprer.maxtuple = max_items_for_showing_in_log  # кортежи
    reprer.maxset = max_items_for_showing_in_log  # множества
    reprer.maxfrozenset = max_items_for_showing_in_log  # замороженные множества
    reprer.maxdeque = max_items_for_showing_in_log
    reprer.maxarray = max_items_for_showing_in_log
    reprer.maxstring = max_items_for_showing_in_log  # строки
    reprer.maxother = max_items_for_showing_in_log  # другие типы данных

    def decorator(func: Callable[..., Any]) -> Callable[..., Any]:

        def output_arguments(*args, **kwargs):
            logger.info(f"\n Начало выполнения {func.__name__}")
            args_repr = reprer.repr(args) if short_input else repr(args)
            kwargs_repr = reprer.repr(kwargs) if short_input else repr(kwargs)
            logger.info(f"In: → {func.__name__} args=({args_repr}) " f"kwargs={kwargs_repr}")

        def output_result(result):
            result_repr = reprer.repr(result) if short_output else repr(result)
            logger.info(f"Out: ← {func.__name__} returned={result_repr!r}")
            logger.info(f"Конец выполнения {func.__name__} \n")

        if iscoroutinefunction(func):

            @wraps(func)
            async def wrapper(*args, **kwargs) -> Any:
                output_arguments(*args, **kwargs)
                result = await func(*args, **kwargs)
                output_result(result)
                return result

        else:

            @wraps(func)
            def wrapper(*args, **kwargs) -> Any:
                output_arguments(*args, **kwargs)
                result = func(*args, **kwargs)
                output_result(result)
                return result

        return wrapper

    return decorator
