# yandex_kinoservice
Киносервис

После создания виртуального окружения и установки всех зависимостей в него - создайте БД postgres локально с такими данными:
```
host: str  =  'localhost'

port: int  =  5432

user: str  =  'postgres'

password: str  =  'postgres'

db_name: str  =  'postgres'
```
Откройте директорию `src/example_application/models.py`
Добавьте туда новую модель:

    class  MyModel(Base):
    
	    __tablename__  =  "my_model"
    
      
    
	    id: Mapped[int] =  mapped_column(primary_key=True)
    
	    some_column: Mapped[str]
    
      
      
    
	    def  __str__(self):
    
		    return  f"example {self.id}"

Перейдите в директорию src

    cd src
Выполните команды:
#аналог python manage.py makemigrations:
`alembic revision --autogenerate -m "создать MyModel в DB"`
#аналог python manage.py migrate
`alembic upgrade head`
