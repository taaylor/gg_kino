import hashlib
import hmac
import logging
import random
import string

from core.config import app_config
from fastapi import HTTPException, status

logger = logging.getLogger(__name__)


class SignedStateManager:
    def __init__(self, secret_key: str):
        """Инициализирует менеджер с секретным ключом."""
        self.secret_key = secret_key.encode("utf-8")

    def generate_state(self) -> str:
        """Возвращает подписанный state."""
        nonce = "".join(random.choice(string.ascii_letters) for _ in range(10))
        signer = hmac.new(self.secret_key, digestmod=hashlib.sha256)
        signer.update(nonce.encode("utf-8"))
        signature = signer.hexdigest()
        return f"{nonce}-{signature}"

    def validate_state(self, state: str) -> bool:
        """Валидирует state."""
        if state.count("-") != 1:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Неверный формат state",
            )
        nonce, signature = state.split("-", 1)
        signer = hmac.new(self.secret_key, digestmod=hashlib.sha256)
        signer.update(nonce.encode("utf-8"))
        expected_signature = signer.hexdigest()
        if not hmac.compare_digest(signature, expected_signature):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Неверная подпись state",
            )
        return True


def get_signed_state_manager() -> SignedStateManager:
    return SignedStateManager(secret_key=app_config.auth_secret_key)


class ApiKeyValidate:

    __slots__ = ()

    @classmethod
    def validate_apikey_service(cls, api_key: str, service_name: str) -> bool:
        if api_key is None and service_name is None:
            logger.debug("Отсутствует API Key или Service Name")
            return False

        logger.info(f"Получен запрос от сервиса {service_name} с APIKEY: {api_key[:5]}***")

        if not hasattr(app_config.apikey, service_name):
            logger.warning(f"Попытка доступа от неизвестного сервиса: {service_name}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Сервис {service_name} не зарегистрирован или неверный API ключ",
            )

        valid_key = getattr(app_config.apikey, service_name)

        if not hmac.compare_digest(api_key, valid_key):
            logger.warning(f"Неверный ключ от сервиса {service_name}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Сервис {service_name} не зарегистрирован или неверный API ключ",
            )

        logger.info(f"Успешная аутентификация сервиса {service_name}")
        return True
