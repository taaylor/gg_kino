# 🎬 Async API сервис

**Асинхронный API-сервис для работы с фильмами, построенный на FastAPI и Elasticsearch.**

---

## 🚀 Быстрый старт

### 🔧 Подготовка окружения

1. **Склонируйте репозиторий**
   ```bash
   git clone https://github.com/taaylor/async_api_module_2.git
   cd async_api_module_2
   ```

2. **Создайте `.env` файл на основе шаблона**
   ```bash
   cp .env.example .env
   ```
   - Отредактируйте `.env`, если необходимо.

### 🏗 Запуск проекта

Запустите сервис с помощью `Docker Compose`:
```bash
docker-compose up --build -d
```

### ✅ Запуск тестов

Тесты запускаются в отдельном окружении, используя `docker-compose-tests.yml` и файл `.env-tests`

Подготовьте `.env-tests` и расположите его в корне проекта `async_api_module_2/` (пример):
```bash
### Переменные для тестирования
# ELASTIC (ESConf)
# TEST_ELASTIC__HOST=elasticsearch-container # Для запуска в контейнере
TEST_ELASTIC__HOST=localhost # Для локального запуска
TEST_ELASTIC__PORT=9200
TEST_ELASTIC__INDEX_FILMS=movies
TEST_ELASTIC__INDEX_GENRES=genres
TEST_ELASTIC__INDEX_PERSONS=persons

# REDIS (RedisConf)
# TEST_REDIS__HOST=redis-container # Для запуска в контейнере
TEST_REDIS__HOST=localhost # Для локального запуска
TEST_REDIS__PORT=6379
TEST_REDIS__DB=0
TEST_REDIS__PASSWORD=Parol123
TEST_REDIS__USER=redis_user
TEST_REDIS_USER__PASSWORD=Parol123

# API (APIConf)
# TEST_API__HOST=theatre-api-container # Для запуска в контейнере
TEST_API__HOST=localhost # Для локального запуска
TEST_API__PORT=8000

##NGINX
TEST_NGINX_PORT=80
##APP DOCKER
TEST_RUN_PORTS=8000

### Переменные для сервиса API
##Приложение
API_UVICORN__HOST=0.0.0.0
API_UVICORN__PORT=8000

##REDIS
API_REDIS__HOST=redis-container
API_REDIS__PORT=6379

##ELASTIC
API_ELASTIC__HOST=elasticsearch-container
API_ELASTIC__PORT=9200
```

Укажите переменные окружения для `API`, `Redis`, `Elasticsearch` и тестируемых индексов.

Для локального запуска переключите `HOST` на `localhost`.

Запуск тестов в контейнере:

```bash
docker compose -f docker-compose-tests.yml --env-file .env-tests up --build -d
```
Остановка тестов и удаление контейнеров:
```bash
docker compose -f docker-compose-tests.yml --env-file .env-tests down
```
Альтернатива: запуск тестов локально (если контейнеры уже работают):
```bash
pytest tests/functional/src/ -rf -v
```

Проект поднимется в контейнерах, включая `API-сервис`, `Elasticsearch` и `Redis`.

### 🔍 Документация API
После запуска сервис будет доступен по адресу:
- Swagger UI: [`http://localhost/api/openapi`](http://localhost/api/openapi)
- OpenAPI JSON: [`http://localhost/api/openapi.json`](http://localhost/api/openapi.json)

---

## 📂 Структура проекта
```
async_api_module_2/
|
├── elastic_dump/             # Дамп данных для Elasticsearch
├── src/
│   ├── api/v1/               # Эндпоинты API
│   ├── core/                 # Конфигурации и логгеры
│   ├── models/               # Pydantic-модели и логика
│   ├── services/             # Бизнес-логика и сервисы
│   ├── utils/                # Утилиты, декораторы
├── tests/
│   └── functional/           # Функциональные тесты проекта
├── .env.example              # Шаблон переменных окружения
├── docker-compose.yml        # Docker Compose для сервиса
├── docker-compose-tests.yml  # Docker Compose для тестов
└── README.md
```

---

## 🛠 Технологии
- **FastAPI** - быстрый и асинхронный веб-фреймворк
- **Elasticsearch** - поисковый движок для хранения и поиска фильмов
- **Docker & Docker Compose** - контейнеризация и управление сервисами
- **Pydantic** - валидация данных
- **Logging** - логирование событий
- **Nginx** - веб-сервер и прокси-сервер
- **Kibana** - тиражируемая свободная программная панель визуализации данных
- **Pytest** - фреймворк для тестирования
- **SOLID** - архитектурные принципы в логике приложения
- **Uvicorn & Gunicorn** - сервер для запуска FastAPI

---

## 👥 Авторы
- **[taaylor](https://github.com/taaylor)**
- **[Potatoes3212](https://github.com/Potatoes3212)**
- **[Kirill67tyar](https://github.com/Kirill67tyar)**
