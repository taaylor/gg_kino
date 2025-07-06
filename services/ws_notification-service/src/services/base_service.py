from storage.cache import Cache


class BaseService:
    """Базовый класс для сервисов, использующих кэширование."""

    __slots__ = ("cache",)

    key_cache_send_event = "send_event:{user_id}:{event_id}"
    key_cache_not_send_event = "not_send_event:{user_id}:{event_id}"

    def __init__(self, cache: Cache):
        self.cache = cache
