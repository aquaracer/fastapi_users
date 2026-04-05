<div align="center">

# User Service

**Асинхронный REST API для регистрации, аутентификации и профиля пользователя**

[![Python](https://img.shields.io/badge/python-3.10%2B-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115-009688?style=for-the-badge&logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com/)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-18-4169E1?style=for-the-badge&logo=postgresql&logoColor=white)](https://www.postgresql.org/)
[![Docker](https://img.shields.io/badge/Docker-Compose-2496ED?style=for-the-badge&logo=docker&logoColor=white)](https://docs.docker.com/compose/)
[![Poetry](https://img.shields.io/badge/Poetry-зависимости-60A5FA?style=for-the-badge&logo=poetry&logoColor=white)](https://python-poetry.org/)
[![SQLAlchemy](https://img.shields.io/badge/SQLAlchemy-2.0-D71F00?style=for-the-badge&logo=sqlalchemy&logoColor=white)](https://www.sqlalchemy.org/)
[![Pydantic](https://img.shields.io/badge/Pydantic-2.x-E92063?style=for-the-badge&logo=pydantic&logoColor=white)](https://docs.pydantic.dev/)
[![structlog](https://img.shields.io/badge/structlog-JSON-111827?style=for-the-badge)](https://www.structlog.org/)
[![Ruff](https://img.shields.io/badge/Ruff-lint-261230?style=for-the-badge&logo=ruff&logoColor=white)](https://docs.astral.sh/ruff/)

</div>

---

## Описание

Микросервис **user-service** — это backend на **FastAPI** с **асинхронным** доступом к **PostgreSQL** через **SQLAlchemy 2**. Реализованы регистрация, вход с ограничением частоты запросов, пара **JWT** (access / refresh), чтение и частичное обновление собственного профиля. Конфигурация задаётся через переменные окружения (**pydantic-settings**), события пишутся в **structlog** (stdout и ротируемый файл).

Базовый префикс API: **`/api/v1`**.

---

## Возможности

| Область | Что есть |
|--------|----------|
| **Аутентификация** | Регистрация, логин, обновление access-токена по refresh; пароли хэшируются (**passlib**) |
| **JWT** | Настраиваемый секрет, алгоритм, время жизни access и refresh |
| **Профиль** | `GET/PATCH /users/me` с Bearer access-токеном |
| **Роли** | `free_user`, `paid_user`, `specialist`, `admin` (enum в БД) |
| **Валидация** | Email, пароль (≥8 символов, не только цифры), телефон в формате `+цифры` |
| **Защита** | **SlowAPI**: лимит на эндпоинт логина (**5 запросов / минуту**) |
| **Логи** | Структурированные JSON-логи (**structlog**), ротация файла |
| **БД** | Миграции **Alembic**, схема `users` с `created_at` / `updated_at` |
| **Инфра** | **Docker Compose**: приложение + PostgreSQL 18 |

---

## Технологический стек

- **Python** 3.11+ (в образе — 3.12)
- **FastAPI**, **Uvicorn**
- **SQLAlchemy 2** (async), **asyncpg**
- **Alembic**
- **Pydantic** / **pydantic-settings**
- **python-jose** (JWT)
- **slowapi** (rate limiting)
- **structlog**
- **Ruff** (dev)
- **Docker**, **Docker Compose**, **Poetry**

---

## Структура проекта

```text
users/
├── main.py                 # Точка входа: FastAPI-приложение, лимитер
├── Dockerfile
├── docker-compose.yml      # backend + PostgreSQL
├── pyproject.toml
├── poetry.lock
├── migrations/             # Alembic
│   ├── env.py
│   └── versions/
│       └── 0001_initial.py
└── src/
    ├── routes.py           # Сборка роутеров: /api/v1
    ├── config/
    │   ├── project_config.py   # Settings из env
    │   ├── limiter.py          # SlowAPI
    │   ├── logger.py           # structlog
    │   └── database/           # Base, engine, сессии
    ├── models/
    │   └── user_model.py       # UserDB, UserRole
    └── users/
        ├── controllers/        # HTTP: auth, users
        ├── services/           # Бизнес-логика
        ├── repositories/       # Доступ к БД
        ├── dependencies/       # DI FastAPI
        ├── schemas/            # Pydantic-схемы
        └── exceptions/         # Доменные ошибки
```

Слои: **контроллер → сервис → репозиторий**; схемы и исключения отделены от транспорта.

---

## API (кратко)

| Метод | Путь | Описание |
|-------|------|----------|
| `POST` | `/api/v1/auth/register` | Регистрация |
| `POST` | `/api/v1/auth/login` | Логин (лимит 5/мин) |
| `POST` | `/api/v1/auth/refresh` | Новый access по refresh |
| `GET` | `/api/v1/users/me` | Текущий пользователь |
| `PATCH` | `/api/v1/users/me` | Частичное обновление профиля |

Интерактивная документация после запуска: **`http://localhost:8000/docs`** (Swagger), **`/redoc`**.

---

## Быстрый старт

### 1. Запуск через Docker Compose

```bash
docker compose up --build
```

### 2. Миграции

```bash
docker exec -it backend poetry run alembic upgrade head
```

Приложение будет доступно по следующим адресам:

    API: http://localhost:8000
    Swagger UI: http://localhost:8000/docs
    ReDoc: http://localhost:8000/redoc

