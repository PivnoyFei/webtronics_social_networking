![FoodgramFastAPI workflow](https://github.com/PivnoyFei/webtronics_social_networking/actions/workflows/main.yml/badge.svg)

<h1 align="center"><a target="_blank" href="">webtronics_social_networking</a></h1>

## Описание
...


### Запуск проекта
Клонируем репозиторий и переходим в него:
```bash
https://github.com/PivnoyFei/webtronics_social_networking.git
cd webtronics_social_networking
```
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

### Запуск проекта
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