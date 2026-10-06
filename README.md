# Splitwiser

A Splitwise-style expense sharing backend, built with FastAPI.

## Setup

Dependencies are managed by [uv](https://docs.astral.sh/uv/). The virtual
environment lives in `.venv/` and `uv` keeps it in sync automatically.

```bash
uv sync          # create/update .venv from pyproject.toml + uv.lock
```

## Running

```bash
uv run uvicorn app.main:app --reload
```

Then:
- http://127.0.0.1:8000/health — health check
- http://127.0.0.1:8000/docs — interactive Swagger UI
- http://127.0.0.1:8000/redoc — alternative API docs

## Tests

```bash
uv run pytest
```

## Adding a dependency

```bash
uv add sqlalchemy          # runtime dependency
uv add --dev ruff          # dev-only dependency
```

## Layout

```
app/
  main.py          # creates the FastAPI app, includes routers
  routers/         # one module per resource
    health.py
    users.py
tests/
docs/              # phase-by-phase learning notes
```

## Endpoints

| Method | Path              | Notes                                  |
| ------ | ----------------- | -------------------------------------- |
| GET    | `/health`         | Liveness probe                         |
| POST   | `/users`          | Create a user; returns `201`           |
| GET    | `/users/{id}`     | Fetch a user; `404` if absent          |

Users are held in memory and are lost on restart — PostgreSQL lands in Phase 3.
