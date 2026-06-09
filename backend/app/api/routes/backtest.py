"""Endpoint de backtesting de estrategias."""
from __future__ import annotations

from fastapi import APIRouter, Query

from ...ml.backtest import StakingMethod, run_backtest
from ...services.backtest_service import generate_history

router = APIRouter(prefix="/backtest", tags=["backtest"])


@router.get("/run")
def backtest(
    initial_bankroll: float = Query(1000.0, gt=0),
    method: str = Query("kelly_fraction", description="kelly|kelly_fraction|fixed|conservative|aggressive"),
    edge_threshold: float = Query(0.02, description="Edge mínimo para apostar (fracción)"),
    compounding: bool = Query(True),
    n: int = Query(600, ge=50, le=5000, description="Tamaño de la muestra histórica"),
):
    """Ejecuta un backtest sobre una muestra histórica reproducible."""
    try:
        staking = StakingMethod(method)
    except ValueError:
        staking = StakingMethod.KELLY_FRACTION

    history = generate_history(n=n)
    result = run_backtest(
        history,
        initial_bankroll=initial_bankroll,
        method=staking,
        edge_threshold=edge_threshold,
        compounding=compounding,
    )
    return result.as_dict()
