# Finance Tracker API — 3-Week Learning Journal

> Coming from Node.js / TypeScript with little Python experience.

---

## What I built

A Personal Finance Tracker REST API — users can register, log in, manage income/expense categories, record transactions, and view monthly summaries. Built over 3 weeks, starting from zero Python knowledge.

| | |
|---|---|
| Language | Python 3.12 |
| Framework | FastAPI + SQLAlchemy async |
| Database | PostgreSQL |
| Tests | 45 passing (41 unit + 4 integration) |
| Coverage | 87% |

---

## Week 1 — Python Fundamentals

The first week was about getting comfortable with Python's mindset, not just learning new syntax. Most things have a direct equivalent in TypeScript but behave slightly differently.

### Checklist

- [x] Python syntax — indentation, `None/True/False`, f-strings, function definitions
- [x] Data structures — `list`, `dict`, `tuple`, `set`
- [x] List comprehension — Pythonic replacement for `.map()` / `.filter()`
- [x] Type hints — annotations, optional values, generics
- [x] Pydantic `BaseModel`, `Field`, `ValidationError` — equivalent to Zod/Joi
- [x] Pydantic `BaseSettings` — load config from `.env`
- [x] Advanced Pydantic — `field_validator`, `model_validator`, nested models
- [x] `async/await` — same syntax as JavaScript, same mental model
- [x] Why sync libraries (like `requests`) block the event loop inside `async def`
- [x] FastAPI route decorators, request body, path/query params, response models
- [x] Dependency injection with `Depends`
- [x] `uv` for package management, `pyproject.toml`, virtual environments
- [x] `ruff` for linting and formatting
- [x] `mypy` for static type checking

### Difficulties

**Indentation as syntax.** Coming from TypeScript where blocks use `{}`, Python uses indentation level to define scope. Forgetting to indent after `if` / `for` / `def` causes `IndentationError`. It feels strange at first but becomes natural quickly.

**`None`, `True`, `False` are capitalised.** Writing `true` or `null` throws a `NameError` at runtime, not a compile-time error. TypeScript would catch this immediately.

**No `const` / `let` / `var`.** Variables are just assigned. Type hints are optional and are not enforced at runtime — `mypy` is the tool that catches type mistakes, but only when you run it explicitly.

---

## Week 2 — Core Features

Week 2 was about building a real project while learning Python's ecosystem. The goal was a fully working API with auth, CRUD, filters, and tests.

### Checklist

- [x] Project scaffold with correct folder structure: `routers / services / repositories / models / schemas / core`
- [x] SQLAlchemy async models for `User`, `Category`, `Transaction`
- [x] Async database session setup with `asyncpg`
- [x] Alembic migrations — `revision --autogenerate` → `upgrade head`
- [x] `POST /auth/register` — password hashing with `bcrypt`, save to DB
- [x] `POST /auth/login` — verify password, return signed JWT
- [x] `get_current_user` dependency for protected routes
- [x] Full CRUD for `Category` and `Transaction`
- [x] Pydantic schemas for all request bodies and response models
- [x] All routes protected — unauthenticated returns 401
- [x] `GET /transactions` filters: `category_id`, `type`, `date_from`, `date_to`
- [x] Unit tests for the service layer
- [x] `ruff` and `mypy` — zero errors
- [x] All endpoints visible in Swagger at `/docs`

### Difficulties

**SQLAlchemy async is a completely different API.** Most tutorials use the sync version. With the async version, every query must be awaited, sessions are `AsyncSession`, and lazy-loading relationships silently crashes. There is no warning — it just throws `MissingGreenlet` at runtime.

**The `expire_on_commit` trap.** After `await db.commit()`, SQLAlchemy expires every attribute on the object, including the primary key. Accessing `obj.id` after committing triggers a lazy reload which fails in async mode. The fix is to read the id before committing.
---

## Week 3 — Production-Ready

Week 3 added the features that turn a working prototype into something you'd actually deploy: proper error handling, structured logging, background tasks, and integration tests.

### Checklist

- [x] `GET /summary?month=YYYY-MM` — income, expense, net balance grouped by month using SQL aggregation
- [x] Pagination on all list endpoints — response shape `{ data, total, limit, offset }`
- [x] Generic `PaginatedResponse[T]` schema
- [x] `category_name` on `TransactionResponse` via Pydantic `AliasPath("category", "name")`
- [x] N+1 query fixed with `selectinload(Transaction.category)`
- [x] Custom exception classes: `NotFoundException`, `BadRequestException`, `UnauthorizedException`, `ConflictException`
- [x] Global exception handlers — consistent error shape `{ error, message, status_code }` across all routes
- [x] Pydantic validators for edge cases: negative amount, invalid date, short password
- [x] `structlog` JSON logging with log level from `.env`
- [x] Pure ASGI request logging middleware — method, path, status, duration logged per request
- [x] `X-Request-ID` UUID injected into every response header and all log entries
- [x] Business event logs: `user_registered`, `transaction_created`, `summary_requested`
- [x] PII removed from logs — email is never logged
- [x] Background task `alert_large_transaction` fires when amount ≥ $10,000 USD without blocking the response
- [x] 4 integration tests against a real PostgreSQL test database
- [x] Session-scoped schema creation (tables created once, not per test)
- [x] Per-test table truncation instead of drop/recreate
- [x] `TEST_DATABASE_URL` loaded from `.env`
- [x] 87% test coverage (target was 70%)
- [x] All 45 tests pass with a single `pytest tests/` command

### Difficulties

**`BaseHTTPMiddleware` breaks async SQLAlchemy.** Starlette's `BaseHTTPMiddleware` runs the handler in a background task internally, which breaks SQLAlchemy's greenlet-based async adapter. Any request that used `selectinload` would crash with `MissingGreenlet`. The fix is to implement a pure ASGI middleware directly — a class with `__call__(self, scope, receive, send)` — which doesn't have this issue.

**N+1 queries are invisible until they aren't.** A list of 20 transactions was firing 21 database queries — one for the list, then one per transaction to load its category name. Nothing in the code looked obviously wrong. `selectinload` fixes this by firing one IN query for all categories at once, always 2 queries regardless of list size.


## After 3 Weeks

Three weeks ago the only Python I knew was that it uses indentation instead of curly braces. By the end I had shipped a production-style API with auth, structured logging, background tasks, and 87% test coverage — all in a language I had never seriously used before.

The most valuable thing wasn't learning the syntax. Syntax is easy to look up. What actually took time was learning where Python's ecosystem draws its lines differently from Node.js. In JavaScript, async is opt-in and most things work in both sync and async contexts without much thought. In Python, the async boundary is strict — the wrong library in the wrong place silently blocks your entire server, or crashes with an error message that takes a while to decode. Once that clicked, a lot of things made more sense.

I also came away with a genuine appreciation for how opinionated the Python tooling has become. `ruff` replaces three or four tools at once and is faster than any of them. `mypy` in strict mode is genuinely useful rather than just noise. Pydantic handles validation, serialisation, and config loading in a way that feels cohesive rather than bolted together. The ecosystem used to have a reputation for fragmentation, but working with these tools didn't feel that way.

If I had to pick one thing I'd do differently, it would be learning SQLAlchemy's async behaviour earlier. Most of the hardest bugs in weeks 2 and 3 — the `MissingGreenlet` errors, the `expire_on_commit` trap, the middleware issue — all traced back to not fully understanding how SQLAlchemy bridges sync ORM code with an async database driver. That is genuinely tricky, and the error messages do not point you in the right direction. Reading the SQLAlchemy async docs properly at the start would have saved several hours.

The project is small by production standards, but every feature here exists in real services: JWT auth, paginated responses, request tracing via IDs in logs, background alerting, isolated integration tests. Building something end-to-end rather than following tutorials was what made it stick.

---

## What to Build Next

**Rate limiting** — prevent brute-force attacks on `/auth/login`. Libraries like `slowapi` wrap existing FastAPI routes with minimal changes. Good introduction to middleware that modifies request flow rather than just observing it.

**Refresh tokens** — the current JWT setup issues one token that expires and cannot be revoked. Adding a refresh token flow teaches token rotation, storing tokens in the database, and invalidating sessions — things every real auth system needs.

**CSV import** — let users bulk-import transactions from a file. Teaches `UploadFile` in FastAPI, streaming large inputs, and row-by-row validation with Pydantic. A natural extension of the current single-transaction create endpoint.

**Real task queue** — replace the in-process `BackgroundTasks` alert with Celery and Redis. The current background task runs inside the same process and dies if the server restarts. This teaches the difference between in-process and out-of-process async work, which is a very common production pattern.

**Summary caching** — `GET /summary` runs aggregation queries on every request. Adding a Redis cache with a short TTL teaches cache invalidation — when a new transaction is created, the cached summary should be cleared. Good introduction to the async Redis client.

**Docker setup** — package the app, PostgreSQL, and Redis into a `docker-compose.yml`. Not a Python feature specifically but a natural production-readiness milestone that makes the project portable and easier to demo.
