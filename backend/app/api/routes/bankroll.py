"""Gestión de bankroll: configuración y cálculo de stake óptimo (Kelly)."""
from __future__ import annotations

from fastapi import APIRouter

from ...ml.kelly import StakingMethod, recommend_stake
from ...schemas import StakeRequest, StakeResponse

router = APIRouter(prefix="/bankroll", tags=["bankroll"])


@router.post("/stake", response_model=StakeResponse)
def calculate_stake(req: StakeRequest):
    """Devuelve el tamaño de apuesta recomendado según el método elegido."""
    try:
        method = StakingMethod(req.method)
    except ValueError:
        method = StakingMethod.KELLY_FRACTION

    rec = recommend_stake(
        prob=req.model_prob,
        odds=req.odds,
        bankroll=req.bankroll,
        method=method,
        fixed_units=req.fixed_units,
    )
    return StakeResponse(**rec.as_dict())
