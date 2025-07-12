from typing import Annotated
from uuid import UUID

from api.v1.schemes import GetAllTemplatesResponse, TemplateRequest, TemplateResponse
from fastapi import APIRouter, Body, Depends, Path
from services.template_service import TemplateService, get_template_service

router = APIRouter()


@router.post(
    path="/template/render/{template_id}",
    summary="Рендеринг HTML-шаблона по идентификатору",
    description="Позволяет отрендерить HTML-шаблон по его идентификатору и переданным параметрам. "
    "Возвращает сгенерированный HTML.",
    response_description="Сгенерированный HTML шаблон",
)
async def render_template(
    template_id: Annotated[UUID, Path(description="Идентификатор шаблона")],
    template_service: Annotated[TemplateService, Depends(get_template_service)],
    params: Annotated[dict, Body(description="Параметры для рендеринга шаблона")] = {},
) -> dict[str, str]:
    template_content = await template_service.render_template_by_id(template_id, params)
    return {"html": template_content}


@router.post(
    path="/template/create",
    summary="Создание нового HTML-шаблона",
    description="Позволяет создать новый HTML-шаблон с указанными параметрами.",
    response_description="Статус создания шаблона",
    response_model=TemplateResponse,
)
async def create_tamplate(
    template_service: Annotated[TemplateService, Depends(get_template_service)],
    request_body: Annotated[TemplateRequest, Body()],
) -> TemplateResponse:
    return await template_service.create_template(request_body)


# TODO: Добавить пагинацию
@router.get(
    path="/templates",
    summary="Получить список шаблонов",
    description="Этот метод возвращает все шаблоны.",
)
async def get_all_templates(
    template_service: Annotated[TemplateService, Depends(get_template_service)],
) -> GetAllTemplatesResponse:
    return await template_service.fetch_templates()
