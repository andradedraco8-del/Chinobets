"""Sistema de alertas.

Genera alertas a partir del estado actual del mercado y del motor:
  - value_bet: aparece una apuesta con valor (edge ≥ umbral)
  - high_confidence: pick de confianza muy alta
  - odds_movement: movimiento significativo de una cuota
  - arbitrage: oportunidad de arbitraje (sobre-cuotas que suman <100%)

En producción se emitirían vía websocket/push; aquí se exponen como feed REST.
"""
from __future__ import annotations

from datetime import datetime

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from ...config import settings
from ...database import get_db
from ...ml.value import implied_probability
from ...models import Match
from ...services.prediction_service import predict_for_match

router = APIRouter(prefix="/alerts", tags=["alerts"])


def _detect_arbitrage(odds: dict) -> float | None:
    """Margen de arbitraje en 1X2 (negativo = oportunidad). None si faltan cuotas."""
    keys = ("home", "draw", "away")
    if not all(odds.get(k) for k in keys):
        return None
    book = sum(implied_probability(odds[k]) for k in keys)
    return round((book - 1.0) * 100, 2)  # <0 ⇒ arbitraje


@router.get("")
def list_alerts(
    min_edge: float = Query(0.05, description="Edge mínimo para alerta de value bet"),
    db: Session = Depends(get_db),
):
    """Feed de alertas calculadas en tiempo real sobre los partidos vigentes."""
    matches = db.query(Match).order_by(Match.kickoff).all()
    alerts: list[dict] = []
    now = datetime.utcnow().isoformat()

    for m in matches:
        pred = predict_for_match(m, settings.DEFAULT_EDGE_THRESHOLD)
        match_name = f"{pred['home']} vs {pred['away']}"

        # Confianza muy alta.
        if pred["confidence_score"] >= 80:
            alerts.append({
                "type": "high_confidence",
                "severity": "info",
                "match_id": m.id,
                "match": match_name,
                "title": "Pick de alta confianza",
                "message": f"{pred['main_pick']['label']} · confianza {pred['confidence_score']:.0f}/100",
                "created_at": now,
            })

        # Value bets relevantes.
        for vb in pred["value_bets"]:
            if vb["is_value"] and vb["edge"] >= min_edge:
                alerts.append({
                    "type": "value_bet",
                    "severity": "success",
                    "match_id": m.id,
                    "match": match_name,
                    "title": f"Value bet · {vb['category']}",
                    "message": f"{vb['selection']} @{vb['odds']:.2f} · edge +{vb['edge_pct']:.1f}%",
                    "created_at": now,
                })

        # Arbitraje.
        arb = _detect_arbitrage({
            "home": m.odds_home, "draw": m.odds_draw, "away": m.odds_away,
        })
        if arb is not None and arb < 0:
            alerts.append({
                "type": "arbitrage",
                "severity": "warning",
                "match_id": m.id,
                "match": match_name,
                "title": "Oportunidad de arbitraje",
                "message": f"Sobre-cuotas 1X2 suman {100 + arb:.1f}% (<100%)",
                "created_at": now,
            })

    # Ordena: éxito (value) primero, luego warning, luego info.
    order = {"success": 0, "warning": 1, "info": 2}
    alerts.sort(key=lambda a: order.get(a["severity"], 3))
    return alerts
