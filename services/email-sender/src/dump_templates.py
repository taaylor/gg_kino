#!/usr/bin/env python3
import asyncio
import logging
from uuid import UUID

from db.postgres import get_async_session
from models.models import Template
from sqlalchemy import select

logger = logging.getLogger(__name__)

HTML_TEMPLATE_MASS_NOTIFY = """
<!DOCTYPE html>
<html>
<body>

 <h1>Привет, {{username}}!</h1>
  <p>Вот список фильмов, которые мы тебе рекомендуем:</p>
  <ul>
    {% for film in recommended_films %}
      <li>
        <strong> {{film.title}} </strong>
        {% if film.imdb_rating is not none %}
          — рейтинг IMDB: {{film.imdb_rating}}
        {% endif %}
      </li>
    {% else %}
      <li>К сожалению, рекомендаций нет.</li>
    {% endfor %}
  </ul>
</body>
</html>

"""
HTML_TEMPLATE_USER_REGISTERED = """
<!DOCTYPE html>
<html>
<body>

<h1>Здравствуйте {{username}}</h1>
<p>Спасибо за регистрацию.</p>
<p>Ссылка на подтверждение почты: {{confirmation_link}}.</p>

</body>
</html>
"""


async def main():
    async for session in get_async_session():
        template = await session.execute(
            select(Template).where(Template.content == HTML_TEMPLATE_USER_REGISTERED)
        )
        if template.scalar_one_or_none():
            logger.info("Шаблон уже есть в базе, выходим.")
            return
        template = await session.execute(
            select(Template).where(Template.content == HTML_TEMPLATE_MASS_NOTIFY)
        )
        if template.scalar_one_or_none():
            logger.info("Шаблон уже есть в базе, выходим.")
            return

        new_template_mass_notify = Template(
            id=UUID("104c743c-030c-41f9-a714-62392a46e71d"),
            name="Mass notify tamplate",
            description="Template for mass notify",
            template_type="MASS-NOTIFY-TYPE",
            content=HTML_TEMPLATE_MASS_NOTIFY,
        )
        new_template_user_registed = Template(
            id=UUID("f69248f5-4f6c-4cd4-82ca-e8f6cd68483f"),
            name="Registration tamplate",
            description="Template for registration",
            template_type="REGISTER-TYPE",
            content=HTML_TEMPLATE_USER_REGISTERED,
        )
        session.add(new_template_mass_notify)
        session.add(new_template_user_registed)
        await session.commit()
        logger.info(f"Добавили новый шаблон с id={new_template_user_registed.id!s}")


if __name__ == "__main__":
    asyncio.run(main())
