#!/usr/bin/env python3
import asyncio
from uuid import UUID

from db.postgres import get_async_session
from models.models import Template
from sqlalchemy import select

# Наш HTML‑шаблон
HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<body>

<h1>Здравствуйте {{username}}</h1>
<p>Спасибо за регистрацию.</p>

</body>
</html>
"""


async def main():
    # Здесь мы используем асинхронный генератор get_async_session,
    # чтобы получить и сразу корректно закрыть сессию.
    async for session in get_async_session():
        # Проверим, нет ли уже такого шаблона
        # exists = await session.execute(
        #     # например, по условию template == 'welcome' или по id
        #     # ниже проверяем по значению самой строки
        #     session.query(Template).filter(Template.template == HTML_TEMPLATE).exists()
        # )
        template = await session.execute(select(Template).where(Template.content == HTML_TEMPLATE))
        if template.scalar_one_or_none():
            print("Шаблон уже есть в базе, выходим.")
            return

        # Создаем новую запись
        new_template = Template(
            # id=uuid.uuid4(),
            id=UUID("f69248f5-4f6c-4cd4-82ca-e8f6cd68483f"),
            content=HTML_TEMPLATE,
        )
        session.add(new_template)
        # Флашим в БД
        await session.commit()
        print(f"Добавили новый шаблон с id={new_template.id!s}")


if __name__ == "__main__":
    asyncio.run(main())
