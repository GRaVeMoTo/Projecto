
* Manage Database Schema revisions *
'''
    uv run alembic revision --autogenerate -m ""
    uv run alembic upgrade head
    uv run alembic downgrade base
'''
