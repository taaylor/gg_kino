from async_fastapi_jwt_auth.exceptions import AuthJWTException
from fastapi import FastAPI, Request, status
from fastapi.encoders import jsonable_encoder
from fastapi.exceptions import RequestValidationError
from starlette.responses import JSONResponse


def setup_exception_handlers(app: FastAPI):

    # обработчик взят из доки:
    # https://fastapi.tiangolo.com/ru/tutorial/handling-errors/#requestvalidationerror
    async def validation_exception_handler(request: Request, exc: RequestValidationError):
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content=jsonable_encoder({"detail": exc.errors(), "body": exc.body}),
        )

    # Обработчик ошибок AuthJWTException
    async def authjwt_exception_handler(request: Request, exc: AuthJWTException):
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={"detail": exc.message},
        )

    app.add_exception_handler(RequestValidationError, validation_exception_handler)
    app.add_exception_handler(AuthJWTException, authjwt_exception_handler)
