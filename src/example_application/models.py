from sqlalchemy.orm import mapped_column, Mapped

# from src.database import Base
from database import Base


class Example(Base):
    __tablename__ = "example"

    id: Mapped[int] = mapped_column(primary_key=True)
    some_column: Mapped[str]


    def __str__(self):
        return f"example {self.id}"
    
class Example_2(Base):
    __tablename__ = "example_2"

    id: Mapped[int] = mapped_column(primary_key=True)
    some_column: Mapped[str]


    def __str__(self):
        return f"example {self.id}"
