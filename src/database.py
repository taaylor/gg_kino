from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker
# from src.core.config import Postgres
from core.config import Postgres


engine = create_async_engine(
    Postgres().DATABASE_URL,
    echo=True,  # включает логирование SQL запросов в консоль
)

# создаём фабрику для генерации сессий (транзакций)
# транзакции - это набор инструкций, которые мы посылаем в БД,
# которые обеспечивают целостность информации
# целостность (атомарность) - или полностью выполняется, или ничего не выполняется
async_session_maker = sessionmaker(
    bind=engine,  # движок, с которым будет связан генератор сессий
    class_=AsyncSession,  # вроде уже не обязательный аргумент 
    expire_on_commit=False,  # закрывать сессию при коммите (завершении транзакции)
)
 
# этот пустой класс используется для миграций
# все модели должны наследоваться от класса этого Base
# и в этом классе аккумулируются данные об моделях
# т.е. сравнивает текущее состояние БД и моделей. 
# Если модели отличаются, то можно сделать миграцию
class Base(DeclarativeBase):
    pass
