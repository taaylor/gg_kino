import asyncio
import time

from connectors import lifespan
from core.config import app_config
from core.logger_config import get_logger, log_call
from db.cache import get_cache
from db.elastic import get_elastic_repository
from extract import get_extractor_films
from load import get_loader_films
from models.models_logic import EmbeddedFilm, FilmLogic
from transform import get_transformer_films

logger = get_logger(__name__)


@log_call
async def main():
    async with lifespan():
        cache = await get_cache()
        elastic_repository = get_elastic_repository()
        if last_run := await cache.get(app_config.last_run_key):
            last_run = int(last_run)
        else:
            last_run = int(time.time() * 1000)
        run_start = int(time.time() * 1000)
        logger.info(f"Время:\n last_run: {last_run} \n run_start: {run_start}")
        extractor = get_extractor_films(elastic_repository)
        transformer = get_transformer_films(
            app_config.template_embedding,
            app_config.embedding_api.url_for_embedding,
        )
        loader = get_loader_films(elastic_repository)
        while True:
            extracted_films: list[FilmLogic] = await extractor.execute_extraction(
                last_run,
                run_start,
                batch_size=10,
            )
            if not len(extracted_films):
                break
            transformed_films: list[EmbeddedFilm] = await transformer.execute_transformation(
                extracted_films
            )
            success_count, errors = await loader.execute_loading(
                films=transformed_films,
                run_start=run_start,
                batch_size=100,
            )
            logger.info(
                (
                    f"Документы успешно обновились в количестве {success_count}"
                    f" количество ошибок: {len(errors)}"
                )
            )
            if errors:
                logger.error(f"Ошибки при обновлении: {errors}")

        await cache.set(
            key=app_config.last_run_key,
            value=str(run_start),
            expire=app_config.cache_expire_in_seconds,
        )
        logger.info(
            (
                "ETL успешно отработал, кол-во шибок <поместить кол-во ошибок>"
                " Новое время сохранено в Redis:"
                f" {app_config.last_run_key} - {run_start}"
            )
        )
    return True


if __name__ == "__main__":
    asyncio.run(main())
