"""Estructuras normalizadas comunes a todos los proveedores."""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime


@dataclass
class NormalizedTeam:
    provider: str
    external_id: str
    name: str
    elo: float = 1500.0
    attack: float = 1.0
    defense: float = 1.0
    xg_for: float = 1.4
    xg_against: float = 1.4


@dataclass
class NormalizedOdds:
    provider: str
    external_id: str
    home: float | None = None
    draw: float | None = None
    away: float | None = None
    over_2_5: float | None = None
    under_2_5: float | None = None
    btts_yes: float | None = None
    btts_no: float | None = None
    bookmaker: str = "consensus"


@dataclass
class NormalizedMatch:
    provider: str
    external_id: str
    league: str
    sport: str
    home: str
    away: str
    kickoff: datetime
    status: str = "scheduled"
    home_score: int | None = None
    away_score: int | None = None
    odds: NormalizedOdds | None = None
    meta: dict = field(default_factory=dict)
