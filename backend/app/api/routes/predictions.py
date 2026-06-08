"""Pronósticos generados por el motor de IA."""
from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from ...config import settings
from ...database import get_db
from ...models import Match
from ...schemas import PredictionOut
from ...services.prediction_service import predict_for_match

router = APIRouter(prefix="/predictions", tags=["predictions"])


@router.get("", response_model=list[PredictionOut])
def all_predictions(db: Session = Depends(get_db)):
    """Pronósticos para todos los partidos programados."""
    matches = db.query(Match).order_by(Match.kickoff).all()
    return [predict_for_match(m, settings.DEFAULT_EDGE_THRESHOLD) for m in matches]


@router.get("/{match_id}", response_model=PredictionOut)
def prediction_for_match(match_id: int, db: Session = Depends(get_db)):
    m = db.query(Match).get(match_id)
    if not m:
        raise HTTPException(status_code=404, detail="Partido no encontrado")
    return predict_for_match(m, settings.DEFAULT_EDGE_THRESHOLD)
