import type { DashboardStats, Prediction, ValueBet } from "./types";

// Datos de respaldo para que el dashboard se renderice sin backend en marcha.
// Coinciden con los valores que produce el motor (backend/app/ml/demo.py).

export const mockStats: DashboardStats = {
  bankroll: 1086.5,
  initial_capital: 1000,
  profit: 86.5,
  roi: 8.65,
  yield_pct: 27.06,
  win_rate: 71.43,
  total_bets: 8,
  won: 5,
  lost: 2,
  pending: 1,
  open_exposure_pct: 5.5,
  growth_curve: [
    { x: 0, bankroll: 1000 },
    { x: 1, bankroll: 1031 },
    { x: 2, bankroll: 1057 },
    { x: 3, bankroll: 1012 },
    { x: 4, bankroll: 1040.5 },
    { x: 5, bankroll: 1064.5 },
    { x: 6, bankroll: 1029.5 },
    { x: 7, bankroll: 1065.5 },
    { x: 8, bankroll: 1086.5 },
  ],
};

export const mockPredictions: Prediction[] = [
  {
    match_id: 1,
    home: "Manchester City",
    away: "Brighton",
    probabilities: {
      "1x2": { home: 0.816, draw: 0.101, away: 0.083 },
      over_under_2_5: { over: 0.78, under: 0.22 },
      btts: { yes: 0.52, no: 0.48 },
      expected_goals: { home: 3.55, away: 0.8 },
      most_likely_score: [3, 0],
    },
    main_pick: { market: "1X2", selection: "home", label: "Gana Manchester City", model_prob: 0.816 },
    confidence_score: 75,
    confidence_text: "Alta",
    explanation:
      "Manchester City presenta un xG promedio de 2.10 y concede 0.95 goles por partido; Brighton genera 1.45 y recibe 1.40. Con ratings ELO de 1685 frente a 1545, el modelo estima los goles esperados en 3.55-0.80. La probabilidad calculada para Manchester City es del 82%. Mejor valor: «Gana Manchester City» a 1.62 (edge 32%).",
    value_bets: [
      { selection_key: "home", selection: "Gana Manchester City", market: "1X2", odds: 1.62, implied_prob: 0.617, model_prob: 0.816, edge: 0.321, edge_pct: 32.1, ev: 0.321, is_value: true, risk_level: "Bajo", category: "Pick Premium", quality_score: 92.4, match: "Manchester City vs Brighton", match_id: 1 },
      { selection_key: "over_2_5", selection: "Más de 2.5 goles", market: "O/U 2.5", odds: 1.7, implied_prob: 0.588, model_prob: 0.78, edge: 0.326, edge_pct: 32.6, ev: 0.326, is_value: true, risk_level: "Bajo", category: "Pick Premium", quality_score: 90.1, match: "Manchester City vs Brighton", match_id: 1 },
    ],
  },
  {
    match_id: 3,
    home: "Real Betis",
    away: "Atletico Madrid",
    probabilities: {
      "1x2": { home: 0.189, draw: 0.22, away: 0.591 },
      over_under_2_5: { over: 0.48, under: 0.52 },
      btts: { yes: 0.51, no: 0.49 },
      expected_goals: { home: 0.91, away: 2.2 },
      most_likely_score: [0, 2],
    },
    main_pick: { market: "1X2", selection: "away", label: "Gana Atletico Madrid", model_prob: 0.591 },
    confidence_score: 58,
    confidence_text: "Media",
    explanation:
      "Real Betis genera un xG de 1.55 y concede 1.30; Atletico Madrid produce 1.80 y recibe 0.90. ELO 1560 vs 1640. Goles esperados 0.91-2.20. Probabilidad de victoria visitante 59%. Mejor valor: «Gana Atletico» a 2.20 (edge 30%).",
    value_bets: [
      { selection_key: "away", selection: "Gana Atletico Madrid", market: "1X2", odds: 2.2, implied_prob: 0.455, model_prob: 0.591, edge: 0.301, edge_pct: 30.1, ev: 0.301, is_value: true, risk_level: "Medio", category: "Pick Premium", quality_score: 81.7, match: "Real Betis vs Atletico Madrid", match_id: 3 },
      { selection_key: "btts_yes", selection: "Ambos marcan: Sí", market: "BTTS", odds: 1.95, implied_prob: 0.513, model_prob: 0.51, edge: 0.056, edge_pct: 5.6, ev: 0.056, is_value: true, risk_level: "Medio", category: "Pick de Valor", quality_score: 41.2, match: "Real Betis vs Atletico Madrid", match_id: 3 },
    ],
  },
  {
    match_id: 2,
    home: "Arsenal",
    away: "Wolves",
    probabilities: {
      "1x2": { home: 0.742, draw: 0.158, away: 0.1 },
      over_under_2_5: { over: 0.66, under: 0.34 },
      btts: { yes: 0.49, no: 0.51 },
      expected_goals: { home: 2.4, away: 0.95 },
      most_likely_score: [2, 0],
    },
    main_pick: { market: "1X2", selection: "home", label: "Gana Arsenal", model_prob: 0.742 },
    confidence_score: 70,
    confidence_text: "Alta",
    explanation:
      "Arsenal domina con xG 1.95 y concede 1.00; Wolves genera 1.20 y recibe 1.45. ELO 1660 vs 1500. Goles esperados 2.40-0.95. Probabilidad victoria local 74%. Mejor valor: «Gana Arsenal» a 1.45 (edge 8%).",
    value_bets: [
      { selection_key: "home", selection: "Gana Arsenal", market: "1X2", odds: 1.45, implied_prob: 0.69, model_prob: 0.742, edge: 0.076, edge_pct: 7.6, ev: 0.076, is_value: true, risk_level: "Bajo", category: "Pick de Valor", quality_score: 56.3, match: "Arsenal vs Wolves", match_id: 2 },
    ],
  },
];

export const mockValueBets: ValueBet[] = mockPredictions
  .flatMap((p) => p.value_bets)
  .sort((a, b) => b.quality_score - a.quality_score);
