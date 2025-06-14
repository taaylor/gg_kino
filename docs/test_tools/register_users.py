import asyncio
import logging

import aiohttp

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

url = "http://localhost/auth/api/v1/sessions/register"

body_template = {
    "username": "username",
    "email": "email",
    "first_name": "string",
    "last_name": "string",
    "gender": "MALE",
    "password": "stringst",
}

# Ограничение на количество одновременно выполняемых задач
SEM_LIMIT = 200  # Максимальное количество параллельных задач
semaphore = asyncio.Semaphore(SEM_LIMIT)


async def send_request(session, i):
    async with semaphore:  # Ограничиваем количество одновременных задач
        name = f"username.{i}"
        email = f"email.{i}"

        body = body_template.copy()
        body["username"] = name
        body["email"] = email

        async with session.post(url, json=body) as response:
            logger.info(f"Итерация: {i}, Статус: {response.status}")


async def main():
    async with aiohttp.ClientSession() as session:
        tasks = [send_request(session, i) for i in range(10000)]
        await asyncio.gather(*tasks)


asyncio.run(main())
