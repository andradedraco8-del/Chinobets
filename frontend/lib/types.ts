export interface DashboardStats {
  bankroll: number;
  initial_capital: number;
  profit: number;
  roi: number;
  yield_pct: number;
  win_rate: number;
  total_bets: number;
  won: number;
  lost: number;
  pending: number;
  open_exposure_pct: number;
  growth_curve: { x: number; bankroll: number }[];
}

export interface ValueBet {
  selection_key: string;
  selection: string;
  market: string;
  odds: number;
  implied_prob: number;
  model_prob: number;
  edge: number;
  edge_pct: number;
  ev: number;
  is_value: boolean;
  risk_level: string;
  category: string;
  quality_score: number;
  match?: string;
  match_id?: number;
}

export interface Prediction {
  match_id: number;
  home: string;
  away: string;
  probabilities: {
    "1x2": { home: number; draw: number; away: number };
    over_under_2_5: { over: number; under: number };
    btts: { yes: number; no: number };
    expected_goals: { home: number; away: number };
    most_likely_score: [number, number];
  };
  main_pick: { market: string; selection: string; label: string; model_prob: number };
  confidence_score: number;
  confidence_text: string;
  explanation: string;
  value_bets: ValueBet[];
}

export interface MarketBreakdown {
  bets: number;
  wins: number;
  win_rate: number;
  staked: number;
  profit: number;
  roi: number;
}

export interface BacktestResult {
  initial_bankroll: number;
  final_bankroll: number;
  profit: number;
  roi: number;
  yield_pct: number;
  win_rate: number;
  total_bets: number;
  wins: number;
  losses: number;
  total_staked: number;
  max_drawdown: number;
  max_drawdown_pct: number;
  longest_losing_streak: number;
  by_market: Record<string, MarketBreakdown>;
  by_sport: Record<string, MarketBreakdown>;
  equity_curve: { x: number; bankroll: number }[];
}

export interface Alert {
  type: "value_bet" | "high_confidence" | "odds_movement" | "arbitrage";
  severity: "success" | "warning" | "info";
  match_id: number;
  match: string;
  title: string;
  message: string;
  created_at: string;
}

export interface StakeResponse {
  method: string;
  kelly_fraction: number;
  stake: number;
  stake_units: number;
  risk_pct: number;
  capped: boolean;
}

export interface Match {
  id: number;
  league: string;
  sport: string;
  home: string;
  away: string;
  kickoff: string;
  status: string;
  odds: Record<string, number>;
}
