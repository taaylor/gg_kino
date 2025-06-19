import pytest_asyncio
from tests.functional.core.logger_conf import get_logger
from tests.functional.core.settings import test_conf
from tests.functional.testdata.model_enum import GenderEnum
from tests.functional.testdata.schemes import LoginRequest, RegisterRequest

logger = get_logger(__name__)


@pytest_asyncio.fixture(name="create_user")
async def create_user(make_post_request):
    async def inner():
        """Отдает токены авторизации, для запросов в API"""

        # Данные для регистрации пользователя
        register_data = RegisterRequest(
            username="test_user",
            email="test_user@mail.ru",
            password="12345678",
            gender=GenderEnum.MALE,
            first_name="Test",
            last_name="User",
        )

        # Пытаемся зарегистрировать пользователя
        register_url = test_conf.authapi.host_service + test_conf.authapi.register_path
        register_body, register_status = await make_post_request(
            url=register_url, data=register_data.model_dump(mode="json")
        )

        # Если регистрация вернула ошибку 400, пытаемся авторизоваться
        if register_status == 400:
            logger.info("Пользователь уже существует, пытаемся авторизоваться")

            login_data = LoginRequest(email=register_data.email, password=register_data.password)

            login_url = test_conf.authapi.host_service + test_conf.authapi.login_path
            login_body, login_status = await make_post_request(
                url=login_url, data=login_data.model_dump(mode="json")
            )

            if login_status != 200:
                raise AssertionError(
                    f"Авторизация завершилась с ошибкой {login_status}: {login_body}"
                )

            body = login_body

        elif register_status == 200:
            logger.info("Пользователь успешно зарегистрирован")
            # При успешной регистрации токены находятся в session
            body = {
                "access_token": register_body["session"]["access_token"],
                "refresh_token": register_body["session"]["refresh_token"],
            }
        else:
            raise AssertionError(
                f"Регистрация завершилась с ошибкой {register_status}: {register_body}"
            )

        if not body:
            raise AssertionError("Не удалось получить токены авторизации")

        access_token = body.get("access_token")
        refresh_token = body.get("refresh_token")

        if not access_token or not refresh_token:
            raise AssertionError(f"Отсутствуют токены в ответе: {body}")

        logger.info(
            f"Пользователь создан, токены получены access={access_token[:5]}, "
            f"refresh={refresh_token[:5]}"
        )

        headers = {
            "access_token": access_token,
            "refresh_token": refresh_token,
        }

        return headers

    return inner
