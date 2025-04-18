from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker
# from src.core.config import Postgres
from core.config import Postgres


engine = create_async_engine(
    Postgres().DATABASE_URL,
    echo=True,
)

async_session_maker = sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
)
 
class Base(DeclarativeBase):
    pass
