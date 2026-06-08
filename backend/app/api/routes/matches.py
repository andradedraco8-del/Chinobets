"""Partidos del día y catálogo deportivo."""
from __future__ import annotations

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from ...database import get_db
from ...models import Match
from ...schemas import MatchOut
from ...services.prediction_service import match_odds

router = APIRouter(prefix="/matches", tags=["matches"])


@router.get("", response_model=list[MatchOut])
def list_matches(
    sport: str | None = Query(None, description="Filtra por deporte"),
    db: Session = Depends(get_db),
):
    q = db.query(Match)
    matches = q.order_by(Match.kickoff).all()
    out = []
    for m in matches:
        if sport and m.league.sport != sport:
            continue
        out.append(
            MatchOut(
                id=m.id,
                league=m.league.name,
                sport=m.league.sport,
                home=m.home_team.name,
                away=m.away_team.name,
                kickoff=m.kickoff,
                status=m.status,
                odds=match_odds(m),
            )
        )
    return out


@router.get("/{match_id}", response_model=MatchOut)
def get_match(match_id: int, db: Session = Depends(get_db)):
    m = db.query(Match).get(match_id)
    if not m:
        from fastapi import HTTPException

        raise HTTPException(status_code=404, detail="Partido no encontrado")
    return MatchOut(
        id=m.id,
        league=m.league.name,
        sport=m.league.sport,
        home=m.home_team.name,
        away=m.away_team.name,
        kickoff=m.kickoff,
        status=m.status,
        odds=match_odds(m),
    )
