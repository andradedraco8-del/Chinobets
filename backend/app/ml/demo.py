"""
Demostración ejecutable del motor de ProTipster AI.

No requiere dependencias externas:

    python backend/app/ml/demo.py
"""
from __future__ import annotations

import json

# Permite ejecutarlo tanto como módulo (`-m`) como script directo.
try:
    from .engine import TeamForm, predict_match
    from .kelly import StakingMethod, portfolio_exposure, recommend_stake
except ImportError:  # ejecución directa
    import os
    import sys

    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    from ml.engine import TeamForm, predict_match
    from ml.kelly import StakingMethod, portfolio_exposure, recommend_stake


def main() -> None:
    bankroll = 1000.0

    fixtures = [
        {
            "home": TeamForm("Manchester City", attack=1.45, defense=0.80, elo=1685, xg_for=2.10, xg_against=0.95),
            "away": TeamForm("Brighton", attack=1.05, defense=1.10, elo=1545, xg_for=1.45, xg_against=1.40),
            "odds": {"home": 1.62, "draw": 4.10, "away": 5.20, "over_2_5": 1.70, "under_2_5": 2.15,
                     "btts_yes": 1.80, "btts_no": 2.00},
        },
        {
            "home": TeamForm("Real Betis", attack=1.10, defense=1.05, elo=1560, xg_for=1.55, xg_against=1.30),
            "away": TeamForm("Atletico Madrid", attack=1.30, defense=0.78, elo=1640, xg_for=1.80, xg_against=0.90),
            "odds": {"home": 3.40, "draw": 3.20, "away": 2.20, "over_2_5": 2.05, "under_2_5": 1.78,
                     "btts_yes": 1.95, "btts_no": 1.85},
        },
    ]

    print("=" * 78)
    print("  ProTipster AI — Demostración del motor de predicción y value bets")
    print(f"  Bankroll: {bankroll:.2f} €")
    print("=" * 78)

    open_stakes: list[float] = []

    for fx in fixtures:
        pred = predict_match(fx["home"], fx["away"], odds=fx["odds"])
        print(f"\n▶ {pred.home}  vs  {pred.away}")
        p = pred.probabilities["1x2"]
        print(f"  1X2  →  L {p['home']*100:5.1f}%  |  X {p['draw']*100:5.1f}%  |  V {p['away']*100:5.1f}%")
        print(f"  Goles esperados: {pred.probabilities['expected_goals']['home']}"
              f"-{pred.probabilities['expected_goals']['away']}"
              f"  (marcador más probable {pred.probabilities['most_likely_score']})")
        print(f"  Pick principal: {pred.main_pick['label']}  "
              f"[confianza {pred.confidence_text} · {pred.confidence_score:.0f}/100]")
        print(f"  IA: {pred.explanation}")

        value = [v for v in pred.value_bets if v["is_value"]]
        if value:
            print("  ★ VALUE BETS detectadas:")
            for v in value:
                stake = recommend_stake(v["model_prob"], v["odds"], bankroll,
                                        method=StakingMethod.KELLY_FRACTION)
                open_stakes.append(stake.stake)
                print(f"    - {v['selection']:<22} cuota {v['odds']:.2f}  "
                      f"edge {v['edge_pct']:+5.1f}%  EV {v['ev']:+.3f}  "
                      f"[{v['category']} · {v['risk_level']}]  "
                      f"→ stake {stake.stake:.2f}€ ({stake.stake_units:.2f}u)")
        else:
            print("  (sin value bets relevantes)")

    print("\n" + "-" * 78)
    print("  Exposición de la cartera:")
    print("  " + json.dumps(portfolio_exposure(open_stakes, bankroll), ensure_ascii=False))
    print("-" * 78)


if __name__ == "__main__":
    main()
