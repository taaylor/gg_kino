COMPOSE_FILE = docker-compose.yml
COMPOSE_FILE_DEBUG = docker-compose.debug.yml
COMPOSE_FILE_TEST = docker-compose-tests.yml

# Можно указать конкретный серви или не указывать и команда будет выполнена для всех сервисов
# Например: make up-logs srv=auth-api
srv ?=

# Запуск контейнеров в фоновом режиме
up:
	docker-compose -f $(COMPOSE_FILE) up -d --build $(srv)

# Остановка контейнеров
down:
	docker-compose -f $(COMPOSE_FILE) down $(srv)

# Остановка контейнеров и удаление волуме
down-v:
	docker-compose -f $(COMPOSE_FILE) down -v $(srv)

# Запустить проект и посмотреть логи опредёлнного сервиса
up-logs:
	docker-compose -f $(COMPOSE_FILE) up -d --build && docker-compose -f $(COMPOSE_FILE) logs -f $(srv)

# Просмотр логов
logs:
	docker-compose -f $(COMPOSE_FILE) logs -f $(srv)

# Запуск тестов async-api
test-async-api:
	docker-compose -f $(COMPOSE_FILE_TEST) --profile async-api-test up --build -d
	docker-compose -f $(COMPOSE_FILE_TEST) logs -f tests-async-api
	docker-compose -f $(COMPOSE_FILE_TEST) --profile async-api-test down -v

# Запуск тестов auth-api
test-auth-api:
	docker-compose -f $(COMPOSE_FILE_TEST) --profile auth-api-test up --build -d
	docker-compose -f $(COMPOSE_FILE_TEST) logs -f tests-auth-api
	docker-compose -f $(COMPOSE_FILE_TEST) --profile auth-api-test down -v
