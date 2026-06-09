"""Endpoints de ingesta de datos externos (sólo rol admin)."""
from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from ...config import settings
from ...core.security import require_roles
from ...database import get_db
from ...models.user import UserRole
from ...services.ingest_service import sync_all

router = APIRouter(prefix="/ingest", tags=["ingest"])


@router.get("/providers")
def providers_status():
    """Estado de configuración de cada proveedor (sin exponer las claves)."""
    return {
        "api_football": bool(settings.API_FOOTBALL_KEY),
        "odds_api": bool(settings.ODDS_API_KEY),
        "sportradar": bool(settings.SPORTRADAR_KEY),
        "thesportsdb": True,  # clave pública disponible
    }


@router.post("/sync")
def sync(
    db: Session = Depends(get_db),
    _: object = Depends(require_roles(UserRole.ADMIN)),
):
    """Lanza una sincronización desde los proveedores configurados."""
    return sync_all(db)
