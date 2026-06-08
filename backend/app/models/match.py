"""Ligas, equipos y partidos."""
from __future__ import annotations

from datetime import datetime

from sqlalchemy import DateTime, Float, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ..database import Base


class League(Base):
    __tablename__ = "leagues"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(120))
    sport: Mapped[str] = mapped_column(String(40), default="football")
    country: Mapped[str] = mapped_column(String(80), default="")
    avg_goals: Mapped[float] = mapped_column(Float, default=1.35)

    teams: Mapped[list["Team"]] = relationship(back_populates="league")


class Team(Base):
    __tablename__ = "teams"

    id: Mapped[int] = mapped_column(primary_key=True)
    league_id: Mapped[int] = mapped_column(ForeignKey("leagues.id"))
    name: Mapped[str] = mapped_column(String(120), index=True)
    elo: Mapped[float] = mapped_column(Float, default=1500.0)
    attack: Mapped[float] = mapped_column(Float, default=1.0)
    defense: Mapped[float] = mapped_column(Float, default=1.0)
    xg_for: Mapped[float] = mapped_column(Float, default=1.4)
    xg_against: Mapped[float] = mapped_column(Float, default=1.4)
    recent_points: Mapped[float] = mapped_column(Float, default=1.5)

    league: Mapped["League"] = relationship(back_populates="teams")


class Match(Base):
    __tablename__ = "matches"

    id: Mapped[int] = mapped_column(primary_key=True)
    league_id: Mapped[int] = mapped_column(ForeignKey("leagues.id"))
    home_team_id: Mapped[int] = mapped_column(ForeignKey("teams.id"))
    away_team_id: Mapped[int] = mapped_column(ForeignKey("teams.id"))
    kickoff: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    status: Mapped[str] = mapped_column(String(20), default="scheduled")
    home_score: Mapped[int | None] = mapped_column(nullable=True)
    away_score: Mapped[int | None] = mapped_column(nullable=True)

    # Cuotas de mercado (decimales) almacenadas para detectar value.
    odds_home: Mapped[float | None] = mapped_column(Float, nullable=True)
    odds_draw: Mapped[float | None] = mapped_column(Float, nullable=True)
    odds_away: Mapped[float | None] = mapped_column(Float, nullable=True)
    odds_over_2_5: Mapped[float | None] = mapped_column(Float, nullable=True)
    odds_under_2_5: Mapped[float | None] = mapped_column(Float, nullable=True)
    odds_btts_yes: Mapped[float | None] = mapped_column(Float, nullable=True)
    odds_btts_no: Mapped[float | None] = mapped_column(Float, nullable=True)

    league: Mapped["League"] = relationship()
    home_team: Mapped["Team"] = relationship(foreign_keys=[home_team_id])
    away_team: Mapped["Team"] = relationship(foreign_keys=[away_team_id])
    predictions: Mapped[list["Prediction"]] = relationship(  # type: ignore[name-defined]
        back_populates="match"
    )
