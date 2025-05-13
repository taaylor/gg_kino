from functools import wraps
from typing import Any, Callable, Coroutine

from opentelemetry import context, trace


def traced(name: str = None) -> Callable:
    """
    Декоратор для трассировки выполнения асинхронных функций с использованием OpenTelemetry.

    Args:
        name (str, optional): Имя для создаваемого спана.
        Если не указано, используется имя декорируемой функции.

    Returns:
        Callable: Декорированная функция, обёрнутая в спан для трассировки.

    Пример использования:
        @traced("custom_span_name")
        async def example_function():
            pass
    """

    def decorator[**P, R](func: Callable) -> Callable[P, Coroutine[Any, Any, R]]:
        @wraps(func)
        async def wrapper(*args: P.args, **kwargs: P.kwargs) -> R | None:
            tracer = trace.get_tracer(__name__)
            current_context = context.get_current()
            with tracer.start_as_current_span(name or func.__name__, current_context):
                return await func(*args, **kwargs)

        return wrapper

    return decorator
