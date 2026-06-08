"""Listado y ranking global de value bets detectadas en todos los partidos."""
from __future__ import annotations

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from ...config import settings
from ...database import get_db
from ...models import Match
from ...schemas import ValueBetOut
from ...services.prediction_service import predict_for_match

router = APIRouter(prefix="/value-bets", tags=["value-bets"])


@router.get("", response_model=list[ValueBetOut])
def value_bets(
    min_edge: float = Query(0.0, description="Edge mínimo (fracción, ej. 0.03 = 3%)"),
    only_value: bool = Query(True, description="Sólo apuestas con valor positivo"),
    db: Session = Depends(get_db),
):
    """Agrega y rankea todas las value bets del día por calidad."""
    matches = db.query(Match).order_by(Match.kickoff).all()
    results: list[dict] = []
    for m in matches:
        pred = predict_for_match(m, settings.DEFAULT_EDGE_THRESHOLD)
        for vb in pred["value_bets"]:
            if vb["edge"] < min_edge:
                continue
            if only_value and not vb["is_value"]:
                continue
            enriched = {**vb, "match": f"{pred['home']} vs {pred['away']}", "match_id": m.id}
            results.append(enriched)
    results.sort(key=lambda x: x["quality_score"], reverse=True)
    return results
