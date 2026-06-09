"""
Motor de predicción (orquestador / ensemble).

Combina los modelos disponibles (Poisson, Dixon-Coles, ELO) en un ensemble
ponderado, calcula el score y la etiqueta de confianza, genera la explicación
en lenguaje natural y produce el análisis de value bet para cada mercado.

Diseñado para ampliarse con modelos ML (Random Forest, XGBoost, LightGBM, redes
neuronales) añadiéndolos al diccionario de modelos con su peso.
"""
from __future__ import annotations

from dataclasses import dataclass, field

from . import dixon_coles, elo, poisson
from .value import ValueAnalysis, analyze_value


# Etiquetas de confianza según el score 0-100.
def confidence_label(score: float) -> str:
    if score >= 80:
        return "Muy alta"
    if score >= 65:
        return "Alta"
    if score >= 50:
        return "Media"
    if score >= 35:
        return "Baja"
    return "Muy baja"


@dataclass
class TeamForm:
    """Datos de entrada de un equipo para alimentar el motor."""

    name: str
    attack: float = 1.0          # fuerza ofensiva relativa (1.0 = media liga)
    defense: float = 1.0         # fuerza defensiva relativa (menor = mejor defensa)
    elo: float = 1500.0
    xg_for: float = 1.4          # goles esperados a favor (media reciente)
    xg_against: float = 1.4      # goles esperados en contra
    recent_points: float = 1.5   # puntos por partido en forma reciente (0-3)


@dataclass
class MatchPrediction:
    home: str
    away: str
    probabilities: dict          # mercado -> probabilidad de cada selección
    main_pick: dict              # selección principal recomendada
    confidence_score: float
    confidence_text: str
    explanation: str
    value_bets: list[dict] = field(default_factory=list)

    def as_dict(self) -> dict:
        return {
            "home": self.home,
            "away": self.away,
            "probabilities": self.probabilities,
            "main_pick": self.main_pick,
            "confidence_score": round(self.confidence_score, 1),
            "confidence_text": self.confidence_text,
            "explanation": self.explanation,
            "value_bets": self.value_bets,
        }


def _blend(dists: list[tuple[dict, float]]) -> dict:
    """Mezcla ponderada de distribuciones 1X2."""
    out = {"home": 0.0, "draw": 0.0, "away": 0.0}
    wsum = sum(w for _, w in dists)
    for d, w in dists:
        for k in out:
            out[k] += d.get(k, 0.0) * w
    if wsum:
        for k in out:
            out[k] /= wsum
    return out


def _ml_probabilities(home: "TeamForm", away: "TeamForm") -> dict | None:
    """Probabilidades 1X2 del modelo ML supervisado, o None si no está listo."""
    try:
        from .features import build_features
        from .ml_models import get_predictor

        predictor = get_predictor()
        if not predictor.ready:
            return None
        return predictor.predict_proba(build_features(home, away))
    except Exception:  # noqa: BLE001
        return None


def predict_match(
    home: TeamForm,
    away: TeamForm,
    odds: dict | None = None,
    league_avg_goals: float = 1.35,
    weights: dict | None = None,
    edge_threshold: float = 0.03,
    use_ml: bool = True,
) -> MatchPrediction:
    """
    Genera la predicción completa de un partido.

    `odds` es un dict de cuotas por selección, ej:
        {"home": 2.10, "draw": 3.30, "away": 3.60,
         "over_2_5": 1.95, "under_2_5": 1.90, "btts_yes": 1.85, "btts_no": 1.95}

    Si `use_ml` y hay un modelo ML entrenado disponible, su predicción 1X2 se
    incorpora al ensemble; en caso contrario sólo intervienen los modelos
    estadísticos (Poisson/Dixon-Coles/ELO).
    """
    weights = weights or {"poisson": 0.25, "dixon_coles": 0.35, "elo": 0.20, "ml": 0.20}

    # Modelo de goles: usa xG reciente para modular ataque/defensa.
    home_attack = home.attack * (home.xg_for / 1.4)
    home_defense = home.defense * (home.xg_against / 1.4)
    away_attack = away.attack * (away.xg_for / 1.4)
    away_defense = away.defense * (away.xg_against / 1.4)

    pois = poisson.predict_poisson(home_attack, home_defense, away_attack, away_defense, league_avg_goals)
    dc = dixon_coles.predict_dixon_coles(home_attack, home_defense, away_attack, away_defense, league_avg_goals)
    elo_probs = elo.elo_match_probabilities(home.elo, away.elo)

    blend_inputs = [
        ({"home": pois.home, "draw": pois.draw, "away": pois.away}, weights.get("poisson", 0.0)),
        ({"home": dc.home, "draw": dc.draw, "away": dc.away}, weights.get("dixon_coles", 0.0)),
        (elo_probs, weights.get("elo", 0.0)),
    ]

    # Aporte del modelo ML (Random Forest / XGBoost / LightGBM) si está listo.
    models_used = ["poisson", "dixon_coles", "elo"]
    ml_probs = None
    if use_ml and weights.get("ml", 0.0) > 0:
        ml_probs = _ml_probabilities(home, away)
        if ml_probs is not None:
            blend_inputs.append((ml_probs, weights["ml"]))
            from .ml_models import get_predictor

            models_used.append(get_predictor().model_name)

    one_x_two = _blend(blend_inputs)

    probabilities = {
        "1x2": {k: round(v, 4) for k, v in one_x_two.items()},
        "over_under_2_5": {"over": round(dc.over_2_5, 4), "under": round(dc.under_2_5, 4)},
        "btts": {"yes": round(dc.btts_yes, 4), "no": round(dc.btts_no, 4)},
        "expected_goals": {
            "home": round(dc.expected_home_goals, 2),
            "away": round(dc.expected_away_goals, 2),
        },
        "most_likely_score": dc.most_likely_score,
        "models": models_used,
    }

    # Selección principal = resultado 1X2 más probable.
    main_sel = max(one_x_two, key=one_x_two.get)
    main_prob = one_x_two[main_sel]
    sel_label = {"home": f"Gana {home.name}", "draw": "Empate", "away": f"Gana {away.name}"}[main_sel]

    # Confianza: probabilidad + acuerdo entre modelos.
    model_spread = max(pois.home, dc.home, elo_probs["home"]) - min(pois.home, dc.home, elo_probs["home"])
    agreement = 1.0 - min(model_spread, 0.5) / 0.5
    confidence_score = min(100.0, main_prob * 70 + agreement * 30)

    main_pick = {
        "market": "1X2",
        "selection": main_sel,
        "label": sel_label,
        "model_prob": round(main_prob, 4),
    }

    # Análisis de value bets sobre todas las cuotas disponibles.
    value_bets: list[dict] = []
    if odds:
        catalog = {
            "home": (one_x_two["home"], f"Gana {home.name}", "1X2"),
            "draw": (one_x_two["draw"], "Empate", "1X2"),
            "away": (one_x_two["away"], f"Gana {away.name}", "1X2"),
            "over_2_5": (dc.over_2_5, "Más de 2.5 goles", "O/U 2.5"),
            "under_2_5": (dc.under_2_5, "Menos de 2.5 goles", "O/U 2.5"),
            "btts_yes": (dc.btts_yes, "Ambos marcan: Sí", "BTTS"),
            "btts_no": (dc.btts_no, "Ambos marcan: No", "BTTS"),
        }
        for key, price in odds.items():
            if key not in catalog or not price:
                continue
            model_prob, label, market = catalog[key]
            va: ValueAnalysis = analyze_value(model_prob, price, edge_threshold)
            entry = {"selection_key": key, "selection": label, "market": market, **va.as_dict()}
            value_bets.append(entry)
        # Ordena por calidad (ranking de picks).
        value_bets.sort(key=lambda x: x["quality_score"], reverse=True)

    explanation = build_explanation(home, away, dc, one_x_two, main_sel, value_bets)

    return MatchPrediction(
        home=home.name,
        away=away.name,
        probabilities=probabilities,
        main_pick=main_pick,
        confidence_score=confidence_score,
        confidence_text=confidence_label(confidence_score),
        explanation=explanation,
        value_bets=value_bets,
    )


def build_explanation(home, away, dc, one_x_two, main_sel, value_bets) -> str:
    """Genera la explicación en lenguaje natural del pronóstico."""
    sel_txt = {"home": home.name, "draw": "el empate", "away": away.name}[main_sel]
    prob = one_x_two[main_sel] * 100
    parts = [
        f"{home.name} presenta un xG promedio de {home.xg_for:.2f} y concede "
        f"{home.xg_against:.2f} goles por partido; {away.name} genera {away.xg_for:.2f} "
        f"y recibe {away.xg_against:.2f}.",
        f"Con ratings ELO de {home.elo:.0f} (local) frente a {away.elo:.0f} (visitante), "
        f"el modelo estima los goles esperados en {dc.expected_home_goals:.2f}-"
        f"{dc.expected_away_goals:.2f}.",
        f"La probabilidad calculada para {sel_txt} es del {prob:.0f}%.",
    ]
    if value_bets:
        top = value_bets[0]
        if top["is_value"]:
            parts.append(
                f"Mejor valor detectado: «{top['selection']}» a cuota {top['odds']:.2f} "
                f"(implícita {top['implied_prob'] * 100:.0f}% vs. modelo "
                f"{top['model_prob'] * 100:.0f}%), un edge de {top['edge_pct']:.1f}% "
                f"clasificado como {top['category']}."
            )
        else:
            parts.append("No se detectan value bets relevantes en las cuotas actuales del mercado.")
    return " ".join(parts)
