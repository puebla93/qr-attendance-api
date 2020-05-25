FROM nginx:latest

ADD nginx.conf /etc/nginx/nginx.conf

RUN mkdir /var/www/static -p

WORKDIR /var/www/static
ADD /static /var/www/static
