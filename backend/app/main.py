"""Punto de entrada de la API de ProTipster AI (FastAPI)."""
from __future__ import annotations

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .api import api_router
from .config import settings
from .database import init_db


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    # Siembra automática si la base está vacía (útil en desarrollo / demo).
    try:
        from .seed import seed_if_empty

        seed_if_empty()
    except Exception as exc:  # pragma: no cover
        print(f"[seed] omitido: {exc}")
    yield


app = FastAPI(
    title=settings.APP_NAME,
    version="0.1.0",
    description="Análisis y pronósticos deportivos profesionales · detección de Value Bets",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router)


@app.get("/health", tags=["system"])
def health():
    return {"status": "ok", "app": settings.APP_NAME, "env": settings.ENV}


@app.get("/", tags=["system"])
def root():
    return {"message": "ProTipster AI API", "docs": "/docs"}
