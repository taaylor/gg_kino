until curl -s http://${ES_HOST}:${ES_PORT}; do
  echo "Waiting for Elasticsearch..."
  sleep 5
done

# movies
elasticdump \
  --input=./movies_settings.json \
  --output=http://${ES_HOST}:${ES_PORT}/movies \
  --type=settings

elasticdump \
  --input=./movies_mapping.json \
  --output=http://${ES_HOST}:${ES_PORT}/movies \
  --type=mapping

elasticdump \
  --input=./movies_data.json \
  --output=http://${ES_HOST}:${ES_PORT}/movies \
  --type=data

# genres
elasticdump \
  --input=./genres_settings.json \
  --output=http://${ES_HOST}:${ES_PORT}/genres \
  --type=settings

elasticdump \
  --input=./genres_mapping.json \
  --output=http://${ES_HOST}:${ES_PORT}/genres \
  --type=mapping

elasticdump \
  --input=./genres_data.json \
  --output=http://${ES_HOST}:${ES_PORT}/genres \
  --type=data

# persons
elasticdump \
  --input=./persons_settings.json \
  --output=http://${ES_HOST}:${ES_PORT}/persons \
  --type=settings

elasticdump \
  --input=./persons_mapping.json \
  --output=http://${ES_HOST}:${ES_PORT}/persons \
  --type=mapping

elasticdump \
  --input=./persons_data.json \
  --output=http://${ES_HOST}:${ES_PORT}/persons \
  --type=data
