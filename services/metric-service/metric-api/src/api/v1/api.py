import logging

from apiflask import APIBlueprint, HTTPError
from flask import request
from models.logic_models import EntryEvent
from service.metric_sender_service import get_metric_processor
from utils.rate_limiter import limiter

from api.v1.schemas import EventRequest

logger = logging.getLogger(__name__)

metric_bp = APIBlueprint("metric", __name__, tag="external-metrics-api")


@metric_bp.post("/metric/")
@limiter.limit("1000 per minute")
@metric_bp.input(EventRequest)
@metric_bp.output({}, status_code=204)
@metric_bp.doc(
    summary="Создание события метрики",
    description="Принимает событие метрики пользователя и отправляет его в Kafka для дальнейшей обработки",  # noqa E501
)
def push_metrics(json_data):
    try:
        event = EntryEvent(**json_data)
        processor = get_metric_processor()
        headers_dict = dict(request.headers)  # Все заголовки

        processor.take_event(event=event, headers=headers_dict)

    except Exception as e:
        logger.exception("При обработке запроса возникла ошибка: %s", str(e))
        raise HTTPError(500, "При обработке запроса возникла ошибка")
