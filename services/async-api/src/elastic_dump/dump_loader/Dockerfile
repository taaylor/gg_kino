FROM node:14

WORKDIR /app

RUN npm install elasticdump -g
COPY ./elastic_dump/dump .
COPY ./elastic_dump/dump_loader/import.sh .
RUN chmod +x /app/import.sh
CMD ["/app/import.sh"]
