import asyncio
import time

from connectors import lifespan
from core.config import app_config
from core.logger_config import get_logger, log_call
from db.cache import get_cache
from db.elastic import get_elastic_repository
from extract import get_extractor_films
from load import get_loader_films
from transform import get_transformer_films

logger = get_logger(__name__)


@log_call(
    short_input=True,
    short_output=True,
    max_items_for_showing_in_log=10,
)
async def main() -> bool:
    """
    Основная функция ETL-процесса: извлечение, преобразование и загрузка данных фильмов.

    Пошагово выполняет:
      1. Устанавливает соединения с Redis и Elasticsearch.
      2. Определяет временные метки last_run (последний запуск) и run_start (текущий запуск).
      3. В цикле:
         a. Извлекает батч фильмов, обновлённых или без embedding (экстракт).
         b. Формирует embedding через внешний сервис (трансформация).
         c. Загружает полученные embedding в Elasticsearch (загрузка).
         d. Суммирует успешные обновления и ошибки, логирует результаты.
      4. Обновляет в Redis метку last_run на текущее время.

    :return: True, если ETL успешно завершился без критических ошибок.
    """
    async with lifespan():
        cache = await get_cache()
        elastic_repository = get_elastic_repository()
        if last_run := await cache.get(app_config.last_run_key):
            last_run = int(last_run)
        else:
            last_run = int(time.time() * 1000)
        run_start = int(time.time() * 1000)
        logger.info(
            (
                f"{main.__name__} начал работу\n"
                f" Время:\n last_run: {last_run} \n run_start: {run_start}"
            )
        )
        extractor = get_extractor_films(elastic_repository)
        transformer = get_transformer_films(
            app_config.template_embedding,
            app_config.embedding_api.url_for_embedding,
        )
        loader = get_loader_films(elastic_repository)
        counter_success = counter_errrors = 0
        while True:
            # извлекаем фильмы
            extracted_films = await extractor.execute_extraction(
                last_run,
                run_start,
                batch_size=app_config.batch_size_etl,
            )
            if not len(extracted_films):
                break
            # преобразуем фильмы
            transformed_films = await transformer.execute_transformation(extracted_films)
            # загружаем фильмы
            success_count, errors = await loader.execute_loading(
                films=transformed_films,
                run_start=run_start,
                batch_size=app_config.batch_size_etl,
            )
            counter_success += success_count
            counter_errrors += len(errors)
            logger.info(
                (
                    f"{main.__name__}: Документы успешно обновились в количестве {success_count}"
                    f" количество ошибок: {len(errors)}"
                )
            )
            if errors:
                logger.error(f"{main.__name__}: Ошибки при обновлении: {errors}")

        await cache.set(
            key=app_config.last_run_key,
            value=str(run_start),
            expire=app_config.cache_expire_in_seconds,
        )
        logger.info(
            (
                f"{main.__name__}: ETL успешно отработал.\n"
                f" Кол-во изменённых документов {counter_success}\n"
                f" Кол-во ошибок {counter_errrors}\n"
                " Новое время сохранено в Redis:"
                f" {app_config.last_run_key} - {run_start}"
            )
        )
    return True


if __name__ == "__main__":
    # это для локального запуска
    # если через docker, то main запускается в tasks.scheduled
    asyncio.run(main())
