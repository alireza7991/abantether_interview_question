set shell := ["bash", "-c"]

run:
    @docker-compose up

run-detached:
    @docker-compose up -d

stop:
    @docker-compose down

build:
    @docker-compose build --no-cache

migrate:
    @docker-compose run aban_api python manage.py migrate

makemigrations:
    @docker-compose run aban_api python manage.py makemigrations

createsuperuser:
    @docker-compose run aban_api python manage.py createsuperuser

test:
    @docker-compose run aban_api python manage.py test

shell:
    @docker-compose run aban_api python manage.py shell

bash:
    @docker-compose run aban_api bash

logs:
    @docker-compose logs

manage cmd:
    @docker-compose run web python manage.py {{cmd}}