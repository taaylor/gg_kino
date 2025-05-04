from functools import wraps
from typing import Annotated, Callable

from fastapi import Depends

from .check_auth import LibAuthJWT, auth_dep


def access_permissions_check(req_permissions: set[str]):
    """Декоратор проверяет наличие у пользователя необходимых пермишенов в access токене"""

    def decorator(func: Callable):
        @wraps(func)
        async def wrapper(*args, authorize: Annotated[LibAuthJWT, Depends(auth_dep)], **kwargs):
            await authorize.jwt_required()
            decrypted_token = await authorize.get_raw_jwt()
            await authorize.compare_permissions(decrypted_token, req_permissions)
            return await func(*args, authorize=authorize, **kwargs)

        return wrapper

    return decorator
