# Mini Social API

`Mini Social API` — це MVP backend-сервіс соціальної платформи.

Реалізовано:
- реєстрацію та авторизацію користувачів;
- роботу з постами;
- лайки/анлайки з ідемпотентною поведінкою;
- нотифікації про лайки через RabbitMQ + окремий worker.

## Технології

- Python 3.12
- FastAPI
- PostgreSQL
- SQLAlchemy 2.0 (async)
- Alembic
- Pydantic v2
- RabbitMQ
- Docker + docker-compose

## Швидкий запуск

1. Заповніть `.env` просто зміннивши `.env.example`:
2. Далі переіменуйте дані для підключення до БД. Для прикладу можна використовувати ці дані: 
Просто скопіюйте і вставте наступні рядки:
```
DB_USER=postgres
DB_PASSWORD=postgres
DB_NAME=postgres
DB_HOST=db
DB_PORT=5432
```
3. Запустіть сервіс:

```bash
docker compose up --build
```

Доступно:
- API: `http://localhost:8000`
- Swagger: `http://localhost:8000/docs`

## Основні можливості

### Auth

- реєстрація за `email + password`;
- хешування пароля через `bcrypt`;
- JWT: `access` + `refresh`;
- оновлення токенів через `/auth/refresh`.

### Posts

- створення, отримання списку, отримання деталей;
- редагування/видалення тільки автором;
- soft delete (`deleted_at`);
- фільтрація, пошук, сортування;
- у відповіді: `author` та `likes_count`.

### Likes

- один користувач може лайкнути пост лише один раз;
- лайк/анлайк ідемпотентні;
- захист від дублювання лайків на рівні БД (`UNIQUE(user_id, post_id)`).

### Notifications (RabbitMQ)

- при лайку публікується подія `post_liked`;
- worker читає подію та пише нотифікацію у таблицю `notifications`;
- доступні ендпоінти:
  - `GET /notifications/`
  - `PATCH /notifications/{id}/read`

## Ендпоінти

### Auth

- `POST /auth/register`
- `POST /auth/login`
- `POST /auth/refresh`

### Posts

- `POST /posts/`
- `GET /posts/`
- `GET /posts/{post_id}`
- `PATCH /posts/{post_id}`
- `DELETE /posts/{post_id}`
- `POST /posts/{post_id}/like`
- `DELETE /posts/{post_id}/like`

### Notifications

- `GET /notifications/`
- `PATCH /notifications/{notification_id}/read`

> Для сумісності також доступні префіксні роути `/api/v1/posts/*` і `/api/v1/notifications/*`.

## Параметри `GET /posts/`

- `limit` — кількість постів (1..100)
- `offset` — зміщення
- `author_id` — фільтр за автором
- `search` — пошук у `title` та `content`
- `sort` — `created_at | likes`
- `order` — `asc | desc`
- `include_deleted` — показувати soft-deleted пости (`true/false`)

Для `GET /posts/{post_id}` також є `include_deleted=true/false`.

## Приклад сценарію перевірки нотифікацій

1. Користувач `A` створює пост.
2. Користувач `B` ставить лайк посту `A`.
3. Користувач `A` викликає `GET /notifications/` і бачить нову нотифікацію.
4. Користувач `A` викликає `PATCH /notifications/{id}/read`.

## HTTP статуси

- `200` — успішна операція
- `201` — створено
- `204` — видалено (soft delete)
- `400` — невалідні дані
- `401` — неавторизований
- `403` — недостатньо прав
- `404` — не знайдено
- `409` — конфлікт (наприклад, email вже існує)

