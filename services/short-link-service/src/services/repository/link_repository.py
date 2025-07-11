import logging

# from datetime import datetime
from functools import lru_cache

# from uuid import UUID
# from zoneinfo import ZoneInfo

# from sqlalchemy import select
# from sqlalchemy.ext.asyncio import AsyncSession
# from sqlalchemy.orm.attributes import flag_modified
# from utils.decorators import sqlalchemy_universal_decorator

logger = logging.getLogger(__name__)


class LinkRepository:
    pass


@lru_cache
def get_link_repository() -> LinkRepository:
    return LinkRepository()
