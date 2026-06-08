"""Configuración de bankroll y apuestas registradas por el usuario."""
from __future__ import annotations

from datetime import datetime

from sqlalchemy import DateTime, Float, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ..database import Base


class BankrollSettings(Base):
    __tablename__ = "bankroll_settings"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), unique=True)
    initial_capital: Mapped[float] = mapped_column(Float, default=1000.0)
    current_capital: Mapped[float] = mapped_column(Float, default=1000.0)
    method: Mapped[str] = mapped_column(String(20), default="kelly_fraction")
    fraction: Mapped[float] = mapped_column(Float, default=0.5)
    unit_pct: Mapped[float] = mapped_column(Float, default=0.01)
    max_exposure_pct: Mapped[float] = mapped_column(Float, default=0.05)

    user: Mapped["User"] = relationship(back_populates="bankroll")  # type: ignore[name-defined]


class Bet(Base):
    __tablename__ = "bets"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    value_bet_id: Mapped[int | None] = mapped_column(ForeignKey("value_bets.id"), nullable=True)
    selection: Mapped[str] = mapped_column(String(80), default="")
    odds: Mapped[float] = mapped_column(Float)
    stake: Mapped[float] = mapped_column(Float)
    status: Mapped[str] = mapped_column(String(20), default="pending")  # pending|won|lost|void
    pnl: Mapped[float] = mapped_column(Float, default=0.0)
    placed_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    settled_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)

    user: Mapped["User"] = relationship(back_populates="bets")  # type: ignore[name-defined]
