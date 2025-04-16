from fastapi import FastAPI
from fastapi.responses import ORJSONResponse
import uvicorn


app = FastAPI(
    title="Read-only API для онлайн-кинотеатра",
    description="Информация о кинопроизведениях, жанрах и персонах, "
    "участвовавших в создании произведения",
    version="1.0.0",
    default_response_class=ORJSONResponse,
)


if __name__ == '__main__':
    uvicorn.run(
        'main:app', host='0.0.0.0', port=8000, reload=True,
    )
# fastapi dev main.py