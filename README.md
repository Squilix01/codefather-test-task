# Mini Social API

`Mini Social API` — це MVP backend-сервіс соціальної платформи.

Реалізовано:
- реєстрацію та авторизацію користувачів;
- роботу з постами;
- ідемпотентні лайки/анлайки;
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

1. Скопіюйте `.env.example` в `.env`.
2. Заповніть змінні підключення до БД (можна взяти із цього прикладу).
```
DB_USER=postgres
DB_PASSWORD=postgres
DB_NAME=postgres
DB_HOST=db
DB_PORT=5432
```
3. Запустіть сервіси:

```bash
docker compose up --build
```

Доступно:
- API: `http://localhost:8000`
- Swagger: `http://localhost:8000/docs`

## Авторизація

Для захищених ендпоінтів передавайте access token у заголовку:

```http
Authorization: Bearer <access_token>
```

## API Reference

### Auth

`POST /auth/register`
- Auth: не потрібен
- Body:
```json
{
  "email": "user@example.com",
  "password": "string"
}
```
- Response `201`:
```json
{
  "id": 1,
  "email": "user@example.com"
}
```

`POST /auth/login`
- Auth: не потрібен
- Body:
```json
{
  "email": "user@example.com",
  "password": "string"
}
```
- Response `200`:
```json
{
  "access_token": "jwt_access_token",
  "refresh_token": "jwt_refresh_token",
  "token_type": "bearer"
}
```

`POST /auth/refresh`
- Auth: не потрібен
- Body:
```json
{
  "refresh_token": "jwt_refresh_token"
}
```
- Response `200`: нова пара `access_token + refresh_token`.

### Posts

`POST /posts/`
- Auth: потрібен
- Body:
```json
{
  "title": "My first post",
  "content": "Hello world"
}
```
- Response `201`: об'єкт поста (`id`, `title`, `content`, `author`, `likes_count`).

`GET /posts/`
- Auth: не потрібен
- Query params:
  - `limit` — скільки постів повернути за один запит. За замовчуванням `10`, максимум `100`.
  - `offset` — скільки постів пропустити від початку списку. Потрібно для пагінації.
  - `author_id` — показати тільки пости конкретного автора.
  - `search` — пошук постів за текстом у `title` і `content`.
  - `sort` — за яким полем сортувати список: за датою створення або за кількістю лайків.
  - `order` — напрямок сортування: від більшого до меншого або навпаки.
  - `include_deleted` — чи включати в результат soft-deleted пости.
- Response `200`: список постів.

`GET /posts/{post_id}`
- Auth: не потрібен
- Path params:
  - `post_id` — ідентифікатор поста.
- Query params:
  - `include_deleted` — чи дозволено повертати soft-deleted пост.
- Response `200`: деталі поста.

`PATCH /posts/{post_id}`
- Auth: потрібен (лише автор поста)
- Path params:
  - `post_id` (`int`)
- Body (можна передати будь-яке поле):
```json
{
  "title": "Updated title",
  "content": "Updated content"
}
```
- Response `200`: оновлений пост.

`DELETE /posts/{post_id}`
- Auth: потрібен (лише автор поста)
- Path params:
  - `post_id` (`int`)
- Body: не потрібен
- Response `204`: без тіла.

### Likes

`POST /posts/{post_id}/like`
- Auth: потрібен
- Path params:
  - `post_id` (`int`)
- Body: не потрібен
- Response `200`:
```json
{
  "status": "ok",
  "action": "liked"
}
```
або
```json
{
  "status": "ok",
  "action": "already_liked"
}
```

`DELETE /posts/{post_id}/like`
- Auth: потрібен
- Path params:
  - `post_id` (`int`)
- Body: не потрібен
- Response `200`:
```json
{
  "status": "ok",
  "action": "unlike"
}
```
або
```json
{
  "status": "ok",
  "action": "already_unliked"
}
```

### Notifications

`GET /notifications/`
- Auth: потрібен
- Body: не потрібен
- Response `200`:
```json
[
  {
    "id": 1,
    "post_id": 10,
    "liked_by_user_id": 2,
    "is_read": false,
    "created_at": "2026-03-24T12:00:00Z"
  }
]
```

`PATCH /notifications/{notification_id}/read`
- Auth: потрібен
- Path params:
  - `notification_id` (`int`)
- Body: не потрібен
- Response `200`:
```json
{
  "message": "Позначено як прочитане"
}
```

## HTTP статуси

- `200` — успішна операція
- `201` — створено
- `204` — видалено
- `400` — невалідні дані
- `401` — неавторизований
- `403` — недостатньо прав
- `404` — не знайдено
- `409` — конфлікт (наприклад, email вже існує)
