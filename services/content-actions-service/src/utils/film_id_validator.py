# Доделать

from functools import lru_cache
from uuid import UUID


class FilmIdValidator:
    """Класс проверяет существует ли запрошенный film_id в базе фильмов сервиса"""

    async def validate_film_id(self, film_id: UUID) -> bool:
        return True


@lru_cache()
def get_film_id_validator():
    return FilmIdValidator()
