
Описание полей таблицы kinoservice.metrics:

id Int64,                       -- идентификатор метрики
user_uuid Nullable(UUID),       -- идентификатор авторизованного пользователя который выполнил событие
film_uuid Nullable(UUID),       -- идентификатор фильма
film_title Nullable(String),    -- наименование фильма
ip_address Nullable(String),    -- ip адрес с которого было выполнено событие
event_type String,              -- тип события (лайк, коммент, др. действие)
message_event String,           -- текст произошедшего события
event_timestamp DateTime,       -- время происхождения события
user_timestamp DateTime         -- время происхождения события на стороне пользователя
