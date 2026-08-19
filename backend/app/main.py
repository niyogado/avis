from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config.settings import settings
from app.routes import auth as auth_router
from app.routes import profile as profile_router
from app.routes import cv as cv_router
from ai.router import router as ai_router

app = FastAPI(title=settings.APP_NAME, version="0.1.0")

# Define allowed origins
allowed_origins = [
    "http://localhost:5173",
    "http://localhost:3000",
    "http://127.0.0.1:5173",
    "http://127.0.0.1:3000",
]

# Include origins from settings if present
if hasattr(settings, "BACKEND_CORS_ORIGINS") and settings.BACKEND_CORS_ORIGINS:
    allowed_origins.extend([str(origin) for origin in settings.BACKEND_CORS_ORIGINS])

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router.router, prefix="/api/auth", tags=["auth"])
app.include_router(profile_router.router, prefix="/api", tags=["profile"])
app.include_router(cv_router.router, prefix="/api", tags=["cv"])
app.include_router(ai_router)

@app.get("/health")
async def health():
    return {"status": "ok"}


@app.get("/")
async def root():
    return {"service": settings.APP_NAME, "status": "ok"}