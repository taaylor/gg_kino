FROM node:14

WORKDIR /app

RUN npm install elasticdump -g

# Копируем содержимое папки backup/elastic_dump/dump/
COPY backup/elastic_dump/dump/ .

# Копируем import.sh из backup/elastic_dump/dump_loader/
COPY backup/elastic_dump/dump_loader/import.sh .

RUN chmod +x /app/import.sh
CMD ["/app/import.sh"]
