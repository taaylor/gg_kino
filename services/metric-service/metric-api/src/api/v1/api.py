import logging

from api.v1.schemas import EventRequest
from apiflask import APIBlueprint, EmptySchema, HTTPError, fields
from flask import request
from models.logic_models import EntryEvent
from service.metric_sender_service import get_metric_processor

logger = logging.getLogger(__name__)


metric_bp = APIBlueprint("metrics", __name__, tag="external-metrics-api")


@metric_bp.post("/metrics/")
@metric_bp.input(EventRequest)
@metric_bp.input({"X-Authorization": fields.String()}, location="headers", validation=False)
@metric_bp.output(EmptySchema, status_code=204)
@metric_bp.doc(
    summary="Метод принимающий метрики",
    description="Метод принимает объект метрики и отправляет его в Kafka",
)
def get_metrics(headers_data, json_data):
    try:
        event = EntryEvent(**json_data)
        processor = get_metric_processor()

        headers_dict = dict(request.headers)
        logger.debug(f"Получен запрос с заголовками: {headers_dict}")

        processor.take_event(event=event, headers=headers_dict)

    except Exception:
        logger.exception("При обработке запроса возникла ошибка")
        raise HTTPError(500, "При обработке запроса возникла ошибка")
