"""Pronósticos generados por el motor y value bets derivadas."""
from __future__ import annotations

from datetime import datetime

from sqlalchemy import DateTime, Float, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ..database import Base


class Prediction(Base):
    __tablename__ = "predictions"

    id: Mapped[int] = mapped_column(primary_key=True)
    match_id: Mapped[int] = mapped_column(ForeignKey("matches.id"))
    market: Mapped[str] = mapped_column(String(40))           # 1X2, O/U 2.5, BTTS…
    selection: Mapped[str] = mapped_column(String(80))        # etiqueta legible
    selection_key: Mapped[str] = mapped_column(String(40), default="")
    model_prob: Mapped[float] = mapped_column(Float)
    confidence_score: Mapped[float] = mapped_column(Float, default=0.0)
    confidence_label: Mapped[str] = mapped_column(String(20), default="Media")
    explanation: Mapped[str] = mapped_column(Text, default="")
    model_name: Mapped[str] = mapped_column(String(40), default="ensemble")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    match: Mapped["Match"] = relationship(back_populates="predictions")  # type: ignore[name-defined]
    value_bet: Mapped["ValueBet"] = relationship(back_populates="prediction", uselist=False)


class ValueBet(Base):
    __tablename__ = "value_bets"

    id: Mapped[int] = mapped_column(primary_key=True)
    prediction_id: Mapped[int] = mapped_column(ForeignKey("predictions.id"))
    bookmaker: Mapped[str] = mapped_column(String(60), default="market")
    odds: Mapped[float] = mapped_column(Float)
    implied_prob: Mapped[float] = mapped_column(Float)
    model_prob: Mapped[float] = mapped_column(Float)
    edge: Mapped[float] = mapped_column(Float)
    ev: Mapped[float] = mapped_column(Float)
    risk_level: Mapped[str] = mapped_column(String(20))
    category: Mapped[str] = mapped_column(String(30))
    quality_score: Mapped[float] = mapped_column(Float, default=0.0)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    prediction: Mapped["Prediction"] = relationship(back_populates="value_bet")
