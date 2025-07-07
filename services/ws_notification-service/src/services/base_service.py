from core.config import app_config
from storage.cache import Cache


class BaseService:
    """Базовый класс для сервисов, использующих кэширование."""

    __slots__ = ("cache",)

    key_event_send = app_config.redis.key_cache_send_event
    key_event_not_send = app_config.redis.key_cache_not_send_event
    key_event_fail = app_config.redis.key_cache_fail_event

    def __init__(self, cache: Cache):
        self.cache = cache
