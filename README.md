[![Build Status](https://github.com/PivnoyFei/webtronics_social_networking/actions/workflows/main.yml/badge.svg?branch=main)](https://github.com/PivnoyFei/webtronics_social_networking/actions/workflows/main.yml)

<h1 align="center"><a target="_blank" href="">webtronics_social_networking</a></h1>

### Стек
![Python](https://img.shields.io/badge/Python-171515?style=flat-square&logo=Python)![3.11](https://img.shields.io/badge/3.11-blue?style=flat-square&logo=3.11)
![FastAPI](https://img.shields.io/badge/FastAPI-171515?style=flat-square&logo=FastAPI)![0.89.1](https://img.shields.io/badge/0.89.1-blue?style=flat-square&logo=0.89.1)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-171515?style=flat-square&logo=PostgreSQL)![13.0](https://img.shields.io/badge/13.0-blue?style=flat-square&logo=13.0)
![SQLAlchemy](https://img.shields.io/badge/SQLAlchemy-171515?style=flat-square&logo=SQLAlchemy)
![Docker](https://img.shields.io/badge/Docker-171515?style=flat-square&logo=Docker)
![Docker-compose](https://img.shields.io/badge/Docker--compose-171515?style=flat-square&logo=Docker)
![Nginx](https://img.shields.io/badge/Nginx-171515?style=flat-square&logo=Nginx)
![GitHub](https://img.shields.io/badge/GitHub-171515?style=flat-square&logo=GitHub)

## Описание
|Название|Метод|Описание|Авторизация|
|--------|-----|--------|-----------|
|/users/signup |POST |Регистрация нового пользователя |Нет
|/users/me |GET |Возвращает самого себя |Да
|/users/&lt;id&gt; |GET |Посмотреть профиль пользователя |Нет
|/users/set_password |PUT |Смена пароля |Да
|/auth/token/login |POST |Авторизация, получение jwt-токена |Нет
|/auth/token/refresh |POST |Обновить токен |Да
|/auth/token/logout |POST |Выйти, удаляет все refresh-токены из бд |Да
|/posts/ |GET |Получение всех записей, реализована пагинация и фильтрация по автору |Нет
|/posts/create |POST |Создание нового поста |Да
|/posts/&lt;id&gt; |GET |Получение деталей поста |Нет
|/posts/&lt;id&gt;/ |PUT |Сообщения редактируются только автором |Да
|/posts/&lt;id&gt;/ |DELETE |Сообщения удаляются только автором |Да
|/posts/&lt;id&gt;/like/ |POST |При создании лайка снимает дизлайк, если есть лайк, то просто удаляет лайк |Да
|/posts/&lt;id&gt;/dislike/|POST |Делает то же самое, что и функция лайка, только с дизлайками |Да


### Запуск проекта
Клонируем репозиторий и переходим в него:
```bash
https://github.com/PivnoyFei/webtronics_social_networking.git
cd webtronics_social_networking
```

## Для выстрого запуска (поднимаем только контейнер бд) создадим виртуальное окружение и установим зависимости:
#### Создаем и активируем виртуальное окружение:
```bash
python3 -m venv venv
source venv/bin/activate
```
#### для Windows
```bash
python -m venv venv
source venv/Scripts/activate
```
#### Обновиляем pip и ставим зависимости из requirements.txt:
```bash
python -m pip install --upgrade pip
pip install -r backend/requirements.txt
```

#### Переходим в папку с файлом docker-compose.yaml:
```bash
cd infra
```

### Перед запуском сервера, в папке infra необходимо создать .env файл со своими данными.
```bash
POSTGRES_DB='postgres' # имя БД
POSTGRES_USER='postgres' # логин для подключения к БД
POSTGRES_PASSWORD='postgres' # пароль для подключения к БД
POSTGRES_SERVER='db' # название контейнера
POSTGRES_PORT='5432' # порт для подключения к БД
ALGORITHM = "HS256"
JWT_SECRET_KEY = "key"
JWT_REFRESH_SECRET_KEY = "key"
```

#### Чтобы сгенерировать безопасный случайный секретный ключ, используйте команду ```openssl rand -hex 32```:


## Быстрый запуск, из контейнеров запускаем только бд:
```bash
docker-compose up -d <название контейнера, например: db>
```

#### Открываем в консоли папку backend и запускаем сервер:
```bash
uvicorn main:app --reload --host 0.0.0.0
```

## Запуск проекта с полной сборкой
```bash
docker-compose up -d --build
```

#### Миграции базы данных (не обязательно):
```bash
docker-compose exec backend alembic revision --message="Initial" --autogenerate
docker-compose exec backend alembic upgrade head
```

#### Останавливаем контейнеры:
```bash
docker-compose down -v
```

#### Автор
[Смелов Илья](https://github.com/PivnoyFei)