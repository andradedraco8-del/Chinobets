"""Configuración central de la aplicación (12-factor, vía variables de entorno)."""
from __future__ import annotations

from functools import lru_cache

try:
    from pydantic_settings import BaseSettings, SettingsConfigDict
except ImportError:  # fallback si sólo está pydantic v1
    from pydantic import BaseSettings  # type: ignore

    SettingsConfigDict = dict  # type: ignore


class Settings(BaseSettings):
    APP_NAME: str = "ProTipster AI"
    ENV: str = "development"
    DEBUG: bool = True

    # Base de datos: PostgreSQL en producción, SQLite por defecto en desarrollo.
    DATABASE_URL: str = "sqlite:///./protipster.db"

    # Cache / colas
    REDIS_URL: str = "redis://localhost:6379/0"

    # Seguridad
    SECRET_KEY: str = "change-me-in-production-please-use-a-long-random-string"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24

    # CORS
    CORS_ORIGINS: list[str] = ["http://localhost:3000", "http://127.0.0.1:3000"]

    # APIs deportivas externas (claves opcionales)
    API_FOOTBALL_KEY: str = ""
    ODDS_API_KEY: str = ""
    SPORTRADAR_KEY: str = ""
    THESPORTSDB_KEY: str = "3"  # clave pública de pruebas

    # The Odds API: deportes/ligas a sincronizar y región de cuotas.
    ODDS_API_SPORTS: list[str] = [
        "soccer_epl",
        "soccer_spain_la_liga",
        "soccer_italy_serie_a",
        "basketball_nba",
    ]
    ODDS_API_REGIONS: str = "eu"

    # Parámetros del motor
    DEFAULT_EDGE_THRESHOLD: float = 0.03
    DEFAULT_MAX_EXPOSURE_PCT: float = 0.05

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
