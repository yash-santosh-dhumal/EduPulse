# Backend

FastAPI backend scaffold for School Sphere.

## What is included

- Application settings
- Database, Redis, and Celery foundation
- JWT/password security helpers
- Alembic migration scaffold
- Initial database schema and demo seed helper
- Health check endpoint
- API router structure
- CI-friendly source layout

## Run locally

1. Create and activate a virtual environment.
2. Install dependencies from `requirements.txt`.
3. Copy `.env.example` to `.env` and adjust values if needed.
4. Create the database schema with Alembic:

```bash
alembic upgrade head
```

5. Seed demo data from a Python shell if needed.
6. Start the app with Uvicorn:

```bash
uvicorn backend.app.main:app --reload
```

## Demo accounts

After seeding, you can sign in with:

- Admin: `admin@example.com` / `Admin@12345`
- Teacher: `teacher@example.com` / `Teacher@12345`
- Student: `student@example.com` / `Student@12345`

## Auth endpoints

- `POST /api/v1/auth/login`
- `POST /api/v1/auth/refresh`
- `POST /api/v1/auth/logout`
- `GET /api/v1/auth/me`
- `GET /api/v1/users`
- `POST /api/v1/users`
- `PUT /api/v1/users/{user_id}`
- `DELETE /api/v1/users/{user_id}`
