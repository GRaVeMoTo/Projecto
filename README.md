# Projecto

A simple yet powerful **Project Management Software** backend API.
Users can create projects, upload documents, and collaborate with others via role-based access control.

## Tech Stack

- **Python 3.14** + **FastAPI**

### Prerequisites

- [uv](https://docs.astral.sh/uv/) installed
- Python 3.14

### Setup

```bash
# Clone and enter project
git clone https://github.com/GRaVeMoTo/Projecto.git
cd Projecto

# Install dependencies
uv sync


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