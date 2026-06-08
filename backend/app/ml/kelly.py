"""
Gestión profesional de bankroll.

Implementa el criterio de Kelly y variantes (fraccional, fijo, conservador,
agresivo) para calcular el tamaño óptimo de cada apuesta, el riesgo por pick y
la exposición total de la cartera.

Kelly clásico:  f* = (b·p - q) / b
  b = cuota - 1 (ganancia neta por unidad)
  p = probabilidad de ganar
  q = 1 - p
"""
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum


class StakingMethod(str, Enum):
    KELLY = "kelly"
    KELLY_FRACTION = "kelly_fraction"
    FIXED = "fixed"
    CONSERVATIVE = "conservative"   # Kelly al 25%
    AGGRESSIVE = "aggressive"       # Kelly al 75%


@dataclass
class StakeRecommendation:
    method: StakingMethod
    kelly_fraction: float      # fracción del bankroll sugerida (0-1)
    stake: float               # importe monetario
    stake_units: float         # en unidades (1 unidad = 1% bankroll por defecto)
    risk_pct: float            # % del bankroll en riesgo
    capped: bool               # True si se aplicó el tope de exposición

    def as_dict(self) -> dict:
        return {
            "method": self.method.value,
            "kelly_fraction": round(self.kelly_fraction, 4),
            "stake": round(self.stake, 2),
            "stake_units": round(self.stake_units, 2),
            "risk_pct": round(self.risk_pct, 2),
            "capped": self.capped,
        }


def kelly_fraction(prob: float, odds: float) -> float:
    """Fracción de Kelly completa. Devuelve 0 si no hay valor (no apostar)."""
    b = odds - 1.0
    if b <= 0:
        return 0.0
    q = 1.0 - prob
    f = (b * prob - q) / b
    return max(0.0, f)


_METHOD_MULTIPLIER = {
    StakingMethod.KELLY: 1.0,
    StakingMethod.KELLY_FRACTION: 0.5,
    StakingMethod.CONSERVATIVE: 0.25,
    StakingMethod.AGGRESSIVE: 0.75,
}


def recommend_stake(
    prob: float,
    odds: float,
    bankroll: float,
    method: StakingMethod = StakingMethod.KELLY_FRACTION,
    fixed_units: float = 1.0,
    unit_pct: float = 0.01,
    max_exposure_pct: float = 0.05,
) -> StakeRecommendation:
    """
    Calcula el stake recomendado.

    - `unit_pct`: tamaño de 1 unidad como fracción del bankroll (1% por defecto).
    - `max_exposure_pct`: tope de riesgo por pick (5% por defecto), evita ruina.
    """
    capped = False

    if method == StakingMethod.FIXED:
        frac = fixed_units * unit_pct
    else:
        full = kelly_fraction(prob, odds)
        frac = full * _METHOD_MULTIPLIER.get(method, 0.5)

    # Tope de exposición por pick.
    if frac > max_exposure_pct:
        frac = max_exposure_pct
        capped = True

    stake = bankroll * frac
    return StakeRecommendation(
        method=method,
        kelly_fraction=frac,
        stake=stake,
        stake_units=stake / (bankroll * unit_pct) if bankroll > 0 else 0.0,
        risk_pct=frac * 100,
        capped=capped,
    )


def portfolio_exposure(stakes: list[float], bankroll: float) -> dict:
    """Exposición total de la cartera de picks abiertos."""
    total = sum(stakes)
    return {
        "total_stake": round(total, 2),
        "exposure_pct": round((total / bankroll * 100) if bankroll else 0.0, 2),
        "open_picks": len(stakes),
        "remaining_bankroll": round(bankroll - total, 2),
    }
