until curl -s http://localhost:9200; do
  echo "Waiting for Elasticsearch..."
  sleep 5
done

# movies
elasticdump \
  --input=http://localhost:9200/movies \
  --output=./extracted_dump/movies_mapping.json \
  --type=mapping

elasticdump \
  --input=http://localhost:9200/movies \
  --output=./extracted_dump/movies_settings.json \
  --type=settings

elasticdump \
  --input=http://localhost:9200/movies \
  --output=./extracted_dump/movies_data.json \
  --type=data

# genres
elasticdump \
  --input=http://localhost:9200/genres \
  --output=./extracted_dump/genres_mapping.json \
  --type=mapping

elasticdump \
  --input=http://localhost:9200/genres \
  --output=./extracted_dump/genres_settings.json \
  --type=settings

elasticdump \
  --input=http://localhost:9200/genres \
  --output=./extracted_dump/genres_data.json \
  --type=data

# persons
elasticdump \
  --input=http://localhost:9200/persons \
  --output=./extracted_dump/persons_mapping.json \
  --type=mapping

elasticdump \
  --input=http://localhost:9200/persons \
  --output=./extracted_dump/persons_settings.json \
  --type=settings

elasticdump \
  --input=http://localhost:9200/persons \
  --output=./extracted_dump/persons_data.json \
  --type=data
