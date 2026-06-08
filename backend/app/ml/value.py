"""
Detección de Value Bets.

El corazón económico de ProTipster AI. Compara la probabilidad estimada por el
modelo con la probabilidad implícita de la cuota de la casa de apuestas.

- probabilidad implícita = 1 / cuota   (antes de quitar el margen)
- edge = prob_modelo * cuota - 1        (ventaja porcentual)
- valor esperado (EV) por unidad apostada = prob_modelo * (cuota - 1) - (1 - prob_modelo)

Si edge > umbral ⇒ value bet.
"""
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum


class RiskLevel(str, Enum):
    LOW = "Bajo"
    MEDIUM = "Medio"
    HIGH = "Alto"
    VERY_HIGH = "Muy alto"


class PickCategory(str, Enum):
    SAFE = "Pick Seguro"
    VALUE = "Pick de Valor"
    PREMIUM = "Pick Premium"
    HIGH_RISK = "Pick de Alto Riesgo"


@dataclass
class ValueAnalysis:
    odds: float
    implied_prob: float
    model_prob: float
    edge: float            # fracción (0.08 = 8%)
    ev: float              # beneficio esperado por unidad
    is_value: bool
    risk_level: RiskLevel
    category: PickCategory
    quality_score: float   # 0-100 para el ranking de picks

    def as_dict(self) -> dict:
        return {
            "odds": round(self.odds, 3),
            "implied_prob": round(self.implied_prob, 4),
            "model_prob": round(self.model_prob, 4),
            "edge": round(self.edge, 4),
            "edge_pct": round(self.edge * 100, 2),
            "ev": round(self.ev, 4),
            "is_value": self.is_value,
            "risk_level": self.risk_level.value,
            "category": self.category.value,
            "quality_score": round(self.quality_score, 1),
        }


def implied_probability(odds: float) -> float:
    """Probabilidad implícita (con margen incluido) de una cuota decimal."""
    return 1.0 / odds if odds > 0 else 0.0


def remove_margin_two_way(odds_a: float, odds_b: float) -> tuple[float, float]:
    """Quita el margen (overround) de un mercado de dos vías -> probabilidades justas."""
    ia, ib = implied_probability(odds_a), implied_probability(odds_b)
    total = ia + ib
    return (ia / total, ib / total) if total else (0.0, 0.0)


def _risk_from(model_prob: float, edge: float) -> RiskLevel:
    if model_prob >= 0.70:
        return RiskLevel.LOW
    if model_prob >= 0.50:
        return RiskLevel.MEDIUM
    if model_prob >= 0.33:
        return RiskLevel.HIGH
    return RiskLevel.VERY_HIGH


def _category_from(model_prob: float, edge: float, risk: RiskLevel) -> PickCategory:
    if edge >= 0.08 and model_prob >= 0.55:
        return PickCategory.PREMIUM
    if model_prob >= 0.70 and edge >= 0.02:
        return PickCategory.SAFE
    if risk in (RiskLevel.HIGH, RiskLevel.VERY_HIGH):
        return PickCategory.HIGH_RISK
    return PickCategory.VALUE


def analyze_value(model_prob: float, odds: float, edge_threshold: float = 0.03) -> ValueAnalysis:
    """Analiza una selección y determina si es value bet, su riesgo y calidad."""
    implied = implied_probability(odds)
    edge = model_prob * odds - 1.0
    ev = model_prob * (odds - 1.0) - (1.0 - model_prob)
    is_value = edge >= edge_threshold

    risk = _risk_from(model_prob, edge)
    category = _category_from(model_prob, edge, risk)

    # Score de calidad: combina edge, confianza del modelo y penaliza cuotas altas.
    edge_component = max(0.0, min(edge, 0.25)) / 0.25 * 55      # hasta 55 pts
    conf_component = model_prob * 35                            # hasta 35 pts
    odds_penalty = max(0.0, (odds - 3.0)) * 2                   # cuotas muy altas penalizan
    quality = max(0.0, min(100.0, edge_component + conf_component + 10 - odds_penalty))

    return ValueAnalysis(
        odds=odds,
        implied_prob=implied,
        model_prob=model_prob,
        edge=edge,
        ev=ev,
        is_value=is_value,
        risk_level=risk,
        category=category,
        quality_score=quality,
    )
