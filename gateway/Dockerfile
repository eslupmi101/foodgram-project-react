FROM nginx:1.22.1

WORKDIR /app

COPY . .

RUN mkdir staticfiles

RUN mkdir mediafiles

COPY nginx.conf /etc/nginx/templates/default.conf.template 
