import asyncio

from core.config import app_config
from core.logger_config import get_logger
from elasticsearch import AsyncElasticsearch

logger = get_logger(__name__)


async def main():
    es = AsyncElasticsearch(app_config.elastic.get_es_host())
    elastic_is_up = await es.ping()
    while True:
        if elastic_is_up:
            logger.info("embedding-etl is working, Elasticsearch allright")
            await es.close()
            break
        logger.info("something goes wrong")


if __name__ == "__main__":
    # logger.info("embedding-etl is working out from main")
    asyncio.run(main())

# def main():
#     logger.info("embedding-etl is working from main")

# if __name__ == "__main__":
#     main()
