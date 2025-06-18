import hashlib
import hmac
import random
import string

from core.config import app_config
from fastapi import HTTPException, status


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
