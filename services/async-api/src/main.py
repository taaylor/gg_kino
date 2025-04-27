from api.v1.filmwork import filmwork
from api.v1.genre import genres
from api.v1.person import persons
from core.config import app_config
from fastapi import FastAPI
from fastapi.responses import ORJSONResponse
from utils import exceptions_handlers
from utils.connectors import lifespan

app = FastAPI(
    title="Read-only API для онлайн-кинотеатра",
    description="Информация о кинопроизведениях, жанрах и персонах, "
    "участвовавших в создании произведения",
    version="1.0.0",
    # Адрес документации в красивом интерфейсе
    docs_url=app_config.docs_url,
    # Адрес документации в формате OpenAPI
    openapi_url=app_config.openapi_url,
    # заменяем стандартный JSON-сериализатор на более шуструю версию, написанную на Rust
    default_response_class=ORJSONResponse,
    lifespan=lifespan,
)


# Подключение обработчиков
exceptions_handlers.setup_exception_handlers(app)

# Секция подключения роутеров к серверу
app.include_router(filmwork.router, prefix="/api/v1/films", tags=["Фильмы"])
app.include_router(persons.router, prefix="/api/v1/persons", tags=["Персоны"])
app.include_router(genres.router, prefix="/api/v1/genres", tags=["Жанры"])
