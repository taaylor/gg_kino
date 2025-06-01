import logging

from api.v1.schemas import EventRequest
from apiflask import APIBlueprint, HTTPError
from flask import request

logger = logging.getLogger(__name__)


metric_bp = APIBlueprint("metrics", __name__, tag="external-metrics-api")


@metric_bp.post("/metrics/")
@metric_bp.input(EventRequest)
@metric_bp.doc(
    summary="Метод принимающий метрики",
    description="Метод принимает объект метрики и отправляет его в Kafka",
)
# @metric_bp.output(EmptySchema, status_code=204)
def get_metrics(json_data):
    try:
        # Получаем заголовки запроса как словарь
        headers_dict = dict(request.headers)

        # Для логирования
        logger.info(f"Получен запрос с заголовками: {headers_dict}")

        # Доступ к конкретным заголовкам
        # user_agent = request.headers.get('User-Agent')
        # content_type = request.headers.get('Content-Type')

        return headers_dict  # Возвращаем заголовки как словарь
    except Exception:
        logger.exception("При обработке запроса возникла ошибка")
        raise HTTPError(500, "При обработке запроса возникла ошибка")
