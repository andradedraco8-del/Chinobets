"""Endpoints de gestión del modelo ML (estado y entrenamiento)."""
from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from ...core.security import require_roles
from ...database import get_db
from ...ml.ml_models import get_predictor
from ...ml.training import train_from_history, train_synthetic
from ...models import Match
from ...models.user import UserRole

router = APIRouter(prefix="/ml", tags=["ml"])


@router.get("/status")
def ml_status():
    """Backend de ML detectado y si el modelo está entrenado."""
    p = get_predictor()
    return {"backend": p.model_name, "available": p.available, "ready": p.ready}


@router.post("/train")
def train(
    source: str = "synthetic",
    db: Session = Depends(get_db),
    _: object = Depends(require_roles(UserRole.ADMIN)),
):
    """Entrena el modelo desde 'synthetic' o 'history' (partidos finalizados)."""
    if source == "history":
        matches = db.query(Match).filter(Match.status == "finished").all()
        return train_from_history(matches)
    return train_synthetic()
