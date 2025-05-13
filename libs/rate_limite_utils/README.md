# Auth Utils

JWT авторизация для сервисов

## Использование
1. Добавить библиотеку при сборке контейнера
```
# Копируем auth_utils и собираем на месте
COPY libs/auth_utils /opt/app/libs/auth_utils
RUN cd /opt/app/libs/auth_utils && poetry build && cd /opt/app && poetry add libs/auth_utils
```
2. Добавить импорт к своему API
```
from auth_utils import LibAuthJWT, auth_dep
```
3. Использовать точно также как
```
from async_fastapi_jwt_auth.auth_jwt import AuthJWTBearer
```
