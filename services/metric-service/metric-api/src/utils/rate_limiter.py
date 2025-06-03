from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

# Создаем limiter без привязки к приложению
limiter = Limiter(
    key_func=get_remote_address,  # Лимитируем по IP
    storage_uri="memory://",
)
