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
    def validate_apikey_service(cls, api_key: str) -> bool:
        api_logs = api_key[:5]
        logger.info(f"Получен запрос от сервиса с APIKEY: {api_logs}***")

        if not (api_key in app_config.api_keys):
            logger.warning(f"Полученый APIKEY невалидный: {api_logs}***")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Переданный API ключ невалидный",
            )

        logger.info(f"Успешная аутентификация по APIKEY: {api_logs}***")
        return True
