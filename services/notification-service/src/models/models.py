import logging

from db.postgres import Base

logger = logging.getLogger(__name__)


class Model(Base):
    """Пример базовой модели"""
