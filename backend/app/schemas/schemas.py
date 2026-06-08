"""Esquemas Pydantic v2 de entrada/salida de la API."""
from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, EmailStr, Field


# ---------- Auth ----------
class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
    role: str


class UserCreate(BaseModel):
    email: EmailStr
    password: str = Field(min_length=6)
    full_name: str = ""


class UserOut(BaseModel):
    id: int
    email: EmailStr
    full_name: str
    role: str

    class Config:
        from_attributes = True


# ---------- Catálogo deportivo ----------
class TeamOut(BaseModel):
    id: int
    name: str
    elo: float
    xg_for: float
    xg_against: float

    class Config:
        from_attributes = True


class MatchOut(BaseModel):
    id: int
    league: str
    sport: str
    home: str
    away: str
    kickoff: datetime
    status: str
    odds: dict


# ---------- Pronósticos ----------
class ValueBetOut(BaseModel):
    selection_key: str
    selection: str
    market: str
    odds: float
    implied_prob: float
    model_prob: float
    edge: float
    edge_pct: float
    ev: float
    is_value: bool
    risk_level: str
    category: str
    quality_score: float
    match: str | None = None
    match_id: int | None = None


class PredictionOut(BaseModel):
    match_id: int
    home: str
    away: str
    probabilities: dict
    main_pick: dict
    confidence_score: float
    confidence_text: str
    explanation: str
    value_bets: list[ValueBetOut]


# ---------- Dashboard ----------
class DashboardStats(BaseModel):
    bankroll: float
    initial_capital: float
    profit: float
    roi: float            # retorno sobre inversión (%)
    yield_pct: float      # beneficio / unidades apostadas (%)
    win_rate: float       # %
    total_bets: int
    won: int
    lost: int
    pending: int
    open_exposure_pct: float
    growth_curve: list[dict]   # [{"x": idx, "bankroll": valor}]


# ---------- Bankroll ----------
class BankrollIn(BaseModel):
    initial_capital: float = 1000.0
    method: str = "kelly_fraction"
    fraction: float = 0.5
    unit_pct: float = 0.01
    max_exposure_pct: float = 0.05


class BankrollOut(BankrollIn):
    current_capital: float


class StakeRequest(BaseModel):
    model_prob: float
    odds: float
    bankroll: float = 1000.0
    method: str = "kelly_fraction"
    fixed_units: float = 1.0


class StakeResponse(BaseModel):
    method: str
    kelly_fraction: float
    stake: float
    stake_units: float
    risk_pct: float
    capped: bool
