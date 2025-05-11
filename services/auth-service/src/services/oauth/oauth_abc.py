from abc import ABC, abstractmethod

import aiohttp


class OAuthBaseService(ABC):

    @abstractmethod
    def create_token_request(self, code: str) -> tuple[str, dict, dict]:
        """Формирует параметры для запроса, на получение access токена (url, data, headers)"""
        pass

    @abstractmethod
    async def get_user_info(self, session: aiohttp.ClientSession, code: str) -> dict:
        """Получает информацию о пользователе, от OAuth-провайдера"""
        pass
