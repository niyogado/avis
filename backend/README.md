# AVIS Core Backend
=================

Minimal FastAPI skeleton for the AVIS Core Backend.

## Quick start
-----------

1. Create a virtual environment and activate it.
2. Install dependencies:

```bash
python3 -m pip install -r backend/requirements.txt
```

3. Copy `.env.example` to `.env` and set real secrets.

4. Run the app:

```bash
uvicorn backend.app.main:app --reload --port 8000
```

## Endpoints

### Defaults
- `/` : basic service info
- `/health` : health check

### Authentication
- POST `/api/auth/register` — Register a new user
- POST `/api/auth/login` — Authenticate a user and obtain an access token
### Profile
- GET `/api/profile/` — Get the authenticated user's profile
- PUT `/api/profile/` — Create or update the authenticated user's profile
### CV
- POST `/api/cv/` — Upload a CV for the authenticated user
- GET `/api/cv/` — Get the authenticated user's CV

Database setup (development)
----------------------------

If you don't yet have migrations applied, you can create tables directly (development only):

```bash
python3 backend/app/scripts/create_tables.py
```

For production use, initialize Alembic and create migrations:

```bash
alembic -c backend/alembic.ini revision --autogenerate -m "create users"
alembic -c backend/alembic.ini upgrade head
```
CV Upload / Storage
-------------------

By default CV files are stored on the local filesystem under the `UPLOAD_DIR` configured in `backend/app/config/settings.py`.
To use S3 instead, set the following environment variables in `.env`:

```
S3_ENABLED=true
S3_BUCKET=your-bucket-name
S3_REGION=your-region
S3_ACCESS_KEY=AKIA...
S3_SECRET_KEY=...
```
> S3 STORAGE is optional you will tell whether it is important.

Upload limits and allowed file types are configurable via `MAX_UPLOAD_SIZE` and `ALLOWED_UPLOAD_TYPES` in settings.

