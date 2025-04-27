# FROM nginx:1.19.3
# FROM nginx:1.22.1
# COPY nginx.conf /etc/nginx/templates/default.conf.template

# FROM nginx:latest
FROM nginx:1.27-alpine
./nginx/nginx.conf:/etc/nginx/nginx.conf:ro
./nginx/configs/site.conf:/etc/nginx/conf.d:ro
