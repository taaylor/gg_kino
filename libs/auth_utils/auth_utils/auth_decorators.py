from functools import wraps
from typing import Annotated, Any, Callable, Coroutine

from fastapi import Depends

from .check_auth import LibAuthJWT, auth_dep


def access_permissions_check(req_permissions: set[str]) -> Callable:
    """Декоратор для проверки наличия у пользователя необходимых
    разрешений (permissions) в access токене.

    Args:
        req_permissions (set[str]): Набор разрешений, которые необходимо проверить у пользователя.

    Returns:
        Callable: Декорированная функция, которая проверяет разрешения перед выполнением.

    Пример использования:
        @access_permissions_check({"READ", "WRITE"})
        async def example_function():
            pass

    """

    def decorator[**P, R](func: Callable) -> Callable[P, Coroutine[Any, Any, R]]:
        @wraps(func)
        async def wrapper(
            *args: P.args,
            authorize: Annotated[LibAuthJWT, Depends(auth_dep)],
            **kwargs: P.kwargs,
        ) -> R | None:
            await authorize.jwt_required()
            decrypted_token = await authorize.get_raw_jwt()
            await authorize.compare_permissions(decrypted_token, req_permissions)
            return await func(*args, authorize=authorize, **kwargs)

        return wrapper

    return decorator
