# Создание Дампа:
## Команда
```bash
elasticdump \
  --input=http://localhost:9200/имя_индекса \
  --output=./имя_индекса_mapping.json \
  --type=mapping
```
```bash
elasticdump \
  --input=http://localhost:9200/имя_индекса \
  --output=./имя_индекса_settings.json \
  --type=settings
```
```bash
elasticdump \
  --input=http://localhost:9200/имя_индекса \
  --output=./имя_индекса_data.json \
  --type=data
```
## Реализация
-----------------------------
movies:
```bash
elasticdump \
  --input=http://localhost:9200/movies \
  --output=./movies_mapping.json \
  --type=mapping
```
```bash
elasticdump \
  --input=http://localhost:9200/movies \
  --output=./movies_settings.json \
  --type=settings
```
```bash
elasticdump \
  --input=http://localhost:9200/movies \
  --output=./movies_data.json \
  --type=data
```
===============
genres:
```bash
elasticdump \
  --input=http://localhost:9200/genres \
  --output=./genres_mapping.json \
  --type=mapping
```
```bash
elasticdump \
  --input=http://localhost:9200/genres \
  --output=./genres_settings.json \
  --type=settings
```
```bash
elasticdump \
  --input=http://localhost:9200/genres \
  --output=./genres_data.json \
  --type=data
```
================
persons:
```bash
elasticdump \
  --input=http://localhost:9200/persons \
  --output=./persons_mapping.json \
  --type=mapping
```
```bash
elasticdump \
  --input=http://localhost:9200/persons \
  --output=./persons_settings.json \
  --type=settings
```
```bash
elasticdump \
  --input=http://localhost:9200/persons \
  --output=./persons_data.json \
  --type=data
```
-------------------------------

# Импорт Дампа:
## Команда
```bash
elasticdump \
  --input=./имя_индекса_settings.json \
  --output=http://новый_хост:9200/имя_индекса \
  --type=settings
```
```bash
elasticdump \
  --input=./имя_индекса_mapping.json \
  --output=http://новый_хост:9200/имя_индекса \
  --type=mapping
```
```bash
elasticdump \
  --input=./имя_индекса_data.json \
  --output=http://новый_хост:9200/имя_индекса \
  --type=data
```
## Реализация
---------------------------------------------------
Порядок выполнения важен

movies:
```bash
elasticdump \
  --input=./movies_settings.json \
  --output=http://localhost:9201/movies \
  --type=settings
```
```bash
elasticdump \
  --input=./movies_mapping.json \
  --output=http://localhost:9201/movies \
  --type=mapping
```
```bash
elasticdump \
  --input=./movies_data.json \
  --output=http://localhost:9201/movies \
  --type=data
```
===============

genres:
```bash
elasticdump \
  --input=./genres_settings.json \
  --output=http://localhost:9201/genres \
  --type=settings
```
```bash
elasticdump \
  --input=./genres_mapping.json \
  --output=http://localhost:9201/genres \
  --type=mapping
```
```bash
elasticdump \
  --input=./genres_data.json \
  --output=http://localhost:9201/genres \
  --type=data
```
=====================

persons:
```bash
elasticdump \
  --input=./persons_settings.json \
  --output=http://localhost:9201/persons \
  --type=settings
```
```bash
elasticdump \
  --input=./persons_mapping.json \
  --output=http://localhost:9201/persons \
  --type=mapping
```
```bash
elasticdump \
  --input=./persons_data.json \
  --output=http://localhost:9201/persons \
  --type=data
```
