# Projecto

A simple yet powerful **Project Management Software** backend API.
Users can create projects, upload documents, and collaborate with others via role-based access control.

## Tech Stack

- **Python 3.14** + **FastAPI**
- **PostgreSQL** + **SQLAlchemy 2.0** (async)
- **Alembic** migrations
- **pyjwt** (JWT) + **argon2-cffi** (password hashing)
- **uv** for dependency management
- **Docker** + **docker-compose**

### Prerequisites

- [uv](https://docs.astral.sh/uv/) installed
- Python 3.14
- PostgreSQL (or use Docker)

### Setup

```bash
# Clone and enter project
git clone https://github.com/GRaVeMoTo/Projecto.git
cd Projecto

# Install dependencies
uv sync

# Edit .env with your DATABASE_URL, JWT_SECRET_KEY, etc.

# Run database migrations
uv run alembic upgrade head

# Start the server
uv run uvicorn projecto.main:app --reload
```

### With Docker

```bash
docker compose up
```

The API will be available at `http://localhost:8000`.
Interactive docs at `http://localhost:8000/docs`.

## Development

```bash
# Run tests
uv run pytest

# Lint & format
uv run ruff check projecto tests
uv run ruff format projecto tests

# Type check
uv run mypy projecto
```

## API Overview

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/auth` | Register new user |
| POST | `/login` | Login, get JWT token |
| POST | `/projects` | Create project |
| GET | `/projects` | List accessible projects |
| GET | `/projects/{id}/info` | Get project details |
| PUT | `/projects/{id}/info` | Update project |
| DELETE | `/projects/{id}` | Delete project (owner only) |
| GET | `/projects/{id}/documents` | List project documents |
| POST | `/projects/{id}/documents` | Upload document(s) |
| GET | `/documents/{id}` | Download document |
| PUT | `/documents/{id}` | Replace document |
| DELETE | `/documents/{id}` | Delete document |
| POST | `/projects/{id}/invite` | Invite user to project (owner only) |
