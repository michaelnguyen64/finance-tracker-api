# Finance Tracker API

A personal finance tracker API for recording and monitoring income and expenses.

## Tech Stack

- Python 3.12
- FastAPI
- SQLAlchemy (async)
- asyncpg
- Alembic
- PostgreSQL
- uv

## Prerequisites

- Python 3.12+
- [uv](https://docs.astral.sh/uv/)
- Docker & Docker Compose

## Local Setup

**1. Clone and install dependencies**

```bash
git clone <repo-url>
cd finance-tracker-api
uv sync
```

**2. Configure environment**

```bash
cp .env.example .env
```

Edit `.env` if your Postgres credentials differ from the defaults.

**3. Start the database**

```bash
docker compose up -d
```

**4. Run migrations**

```bash
uv run alembic upgrade head
```

**5. Start the server**

```bash
uv run uvicorn app.main:app --reload
```

API is available at `http://localhost:8000`
Swagger UI at `http://localhost:8000/docs`

## Database Migrations

After changing a model, generate and apply a new migration:

```bash
uv run alembic revision --autogenerate -m "describe the change"
uv run alembic upgrade head
```

To rollback the last migration:

```bash
uv run alembic downgrade -1
```

## Project Structure

```
app/
├── routers/        # route handlers
├── services/       # business logic
├── repositories/   # database queries
├── models/         # SQLAlchemy models
├── schemas/        # Pydantic request/response schemas
└── core/           # config, db session, security
alembic/            # migration files
tests/              # test suite
```

## Running Tests

```bash
uv run pytest
```
