AVIS Core Backend
=================

Minimal FastAPI skeleton for the AVIS Core Backend.

Quick start
-----------

1. Create a virtual environment and activate it.
2. Install dependencies:

```bash
python -m pip install -r backend/requirements.txt
```

3. Copy `.env.example` to `.env` and set real secrets.

4. Run the app:

```bash
uvicorn backend.app.main:app --reload --port 8000
```

Endpoints
- `/` : basic service info
- `/health` : health check

Database setup (development)
----------------------------

If you don't yet have migrations applied, you can create tables directly (development only):

```bash
python backend/app/scripts/create_tables.py
```

For production use, initialize Alembic and create migrations:

```bash
alembic -c backend/alembic.ini revision --autogenerate -m "create users"
alembic -c backend/alembic.ini upgrade head
```
