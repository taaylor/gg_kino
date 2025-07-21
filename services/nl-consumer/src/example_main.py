import json
import logging

import httpx
from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

logger = logging.getLogger(__name__)


class QueryRequest(BaseModel):
    query: str


genres = ["комедия", "фантастика", "драма", "ужасы", "боевик"]
themes = ["будущее", "любовь", "приключения", "война", "история"]

json_string = """
{
    "genre": "string или null",
    "theme": "string или null",
    "has_genre": "boolean",
    "has_theme": "boolean",
    "genres_score": "float 0–1",
    "themes_score": "float 0–1",
    "status": "string"
}
"""

format = {
    "type": "object",
    "properties": {
        "genre": {
            "type": ["string", "null"],
            "description": "Выбранный жанр или null, если жанр не указан.",
        },
        "theme": {
            "type": ["string", "null"],
            "description": "Выбранная тематика или null, если тематика не указана.",
        },
        "has_genre": {"type": "boolean", "description": "True, если жанр указан, иначе false."},
        "has_theme": {
            "type": "boolean",
            "description": "True, если тематика указана, иначе false.",
        },
        "genres_scores": {
            "type": "number",
            "minimum": 0,
            "maximum": 1,
            "description": "Максимальное значение косинусного сходства для жанра (от 0 до 1).",
        },
        "theme_scores": {
            "type": "number",
            "minimum": 0,
            "maximum": 1,
            "description": "Максимальное значение косинусного сходства для тематики (от 0 до 1).",
        },
        "status": {
            "type": "string",
            "description": "Статус обработки запроса или сообщение для пользователя.",
        },
    },
    "required": ["has_genre", "has_theme", "genres_scores", "theme_scores", "status"],
}


async def analyze_query(query: str):
    prompt = f"""
    Ты работаешь в рекомендательной системе кинотеатра.
    Твоя задача определить достаточно ли информации предоставил пользователь в описании тематики, которую хочет сегодня посмотреть.
    Анализируй запрос пользователя, чтобы определить, указаны ли жанр фильма (из списка: {genres}) и тематика.
    Если пользователь предоставил запрос из которого косвенно можно понять тематику и жанр, то предугадай их самостоятельно.

    Верни ответ в формате JSON со следующими полями:

    - "genre": строка, выбранный жанр или null, если жанр не указан.
    - "theme": строка, выбранная тематика или null, если тематика не указана.
    - "has_genre": boolean, true, если жанр указан, иначе false.
    - "has_theme": boolean, true, если тематика указана, иначе false.
    - "genres_scores": число, максимальное значение косинусного сходства для жанра (от 0 до 1).
    - "theme_scores": число, максимальное значение косинусного сходства для тематики (от 0 до 1).
    - "status": строка, "OK", если оба поля (has_genre, has_theme) — true.
        Иначе напиши в значение "status" просьбу к пользователю для уточнения его запроса.
        Обращайся к пользователю уважительно и нежно, на "Вы", на русском языке, твоя просьба должна быть не больше 300 символов.

    Ответ должен абсолютно строго соответствовать этой json модели, никаких других атрибутов и слов в ответе не должно быть.

    Для оценки сходства сравни запрос с каждым жанром и тематикой, используя семантическое понимание. Укажи максимальное значение сходства для жанра и тематики (примерно оцени, от 0 до 1).
    Если жанр или тематика не упоминаются явно, установи соответствующее значение has_genre или has_theme в false и score в 0.

    Запрос: "{query}"
    """  # noqa: E501

    async with httpx.AsyncClient(timeout=httpx.Timeout(30)) as client:
        data = {"model": "llama3", "prompt": prompt, "stream": False, "format": format}
        headers = {"Content-Type": "application/json"}
        url = "http://localhost:11434/api/generate"

        logger.info(f"Запрашиваю ответ от LLM prompt: {prompt}")
        response = await client.post(url=url, json=data, headers=headers)
        response.raise_for_status()
        try:
            response_data = response.json()
            logger.info(f"LLM вернула ответ: {response_data}")
            return json.loads(response_data["response"])
        except json.JSONDecodeError:
            return {
                "genre": None,
                "theme": None,
                "has_genre": False,
                "has_theme": False,
                "genres_scores": 0.0,
                "theme_scores": 0.0,
                "status": "Ошибка при обработке запроса. Пожалуйста, попробуйте ещё раз.",
            }
