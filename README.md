[![Foodgram workflow](https://github.com/Ker-r/foodgram-project-react/actions/workflows/foodgram.yml/badge.svg)](https://github.com/Ker-r/foodgram-project-react/actions/workflows/foodgram.yml)

http://84.201.143.128/

## Описание проекта 
Приложение «Продуктовый помощник»: сайт, на котором пользователи могут публиковать рецепты, добавлять чужие рецепты в избранное и подписываться на публикации других авторов, а также создавать список покупок и загружать его в pdf формате.

### шаблон наполнения env-файла:
- DB_ENGINE=django.db.backends.postgresql # указываем, что работаем с postgresql
- DB_NAME=postgres # имя базы данных
- POSTGRES_USER=postgres # логин для подключения к базе данных
- POSTGRES_PASSWORD=postgres # пароль для подключения к БД (установите свой)
- DB_HOST=db # название сервиса (контейнера)
- DB_PORT=5432 # порт для подключения к БД

### описание команд для запуска приложения в контейнерах
- docker ps # показывает список запущенных контейнеров
- docker pull #  скачать определённый образ или набор образов
- docker build # собирает образ Docker из Dockerfile и «контекста»
- docker run # запускает контейнер, на основе указанного образа
- docker logs # команда используется для просмотра логов указанного контейнера
- docker volume ls # показывает список томов, которые являются предпочитаемым механизмом для сохранения данных, генерируемых и используемых контейнерами Docker
- docker rm # удаляет один и более контейнеров
- docker rmi # удаляет один и более образов
- docker stop # останавливает один и более контейнеров
- docker-compose up -d --build # пересборка контейнера

### описание команды для заполнения базы данными
- sudo docker-compose exec backend python manage.py collectstatic --no-input
- sudo docker-compose exec backend python manage.py makemigrations recipes
- sudo docker-compose exec backend python manage.py makemigrations users
- sudo docker-compose exec backend python manage.py migrate
- sudo docker-compose exec backend python manage.py createsuperuser
- sudo docker-compose exec backend python manage.py ingredients_load
- sudo docker-compose exec backend python manage.py tags_load
- sudo docker-compose exec backend python manage.py dumpdata > fixtures.json

### Тестовый пользователь 
Суперюзер
Username: Ker
Email: ker.stiv@yandex.ru
Password: Admin12345

