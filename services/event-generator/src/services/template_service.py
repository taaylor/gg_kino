import logging
from typing import Annotated
from uuid import UUID

from api.v1.schemes import GetAllTemplatesResponse, TemplateRequest, TemplateResponse
from db.postgres import get_session
from fastapi import Depends, HTTPException, status
from jinja2 import Template as JinjaTemplate
from models.models import Template as TemplateModel
from services.repository.tamplate_repository import TemplateRepository, get_template_repository
from sqlalchemy.ext.asyncio import AsyncSession

logger = logging.getLogger(__name__)


class TemplateService:

    def __init__(self, repository: TemplateRepository, session: AsyncSession):
        self.repository = repository
        self.session = session

    async def render_template_by_id(
        self,
        template_id: UUID,
        params: dict,
    ) -> str:

        template = await self.repository.fetch_template_by_id(self.session, template_id)
        if not template:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Шаблон не найден")
        jinja_template = JinjaTemplate(template.content)
        return jinja_template.render(**params)

    async def create_template(self, request_body: TemplateRequest) -> TemplateResponse:
        template = TemplateModel(
            description=request_body.description,
            template_type=request_body.template_type,
            content=request_body.content,
            name=request_body.name,
        )
        template_create = await self.repository.create_or_update_object(self.session, template)
        return TemplateResponse.model_validate(template_create)

    async def fetch_templates(self) -> GetAllTemplatesResponse:
        logger.info("Поступил запрос на получение всех шаблонов")

        templates = await self.repository.fetch_all_from_db(self.session)

        if templates:
            logger.info(f"Получен список из: {len(templates)} шаблонов")

            return GetAllTemplatesResponse(
                templates=[TemplateResponse.model_validate(template) for template in templates]
            )

        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Не найдено ни одного шаблона"
        )


def get_template_service(
    repository: Annotated[TemplateRepository, Depends(get_template_repository)],
    session: Annotated[AsyncSession, Depends(get_session)],
) -> TemplateService:
    return TemplateService(repository, session)
