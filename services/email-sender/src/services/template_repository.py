from uuid import UUID

from db.postgres import get_async_session
from models.models import Template
from sqlalchemy import select


class TamplateRepository:
    async def get_tamplate_by_id(self, template_id: UUID) -> Template | None:
        async for session in get_async_session():
            return (
                await session.execute(select(Template).where(Template.id == template_id))
            ).scalar_one_or_none()


def get_tamplate_repository() -> TamplateRepository:
    return TamplateRepository()
