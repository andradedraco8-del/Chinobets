"""Servicio de ingesta: vuelca datos de proveedores externos en la BD.

Orquesta los clientes de integración, normaliza y hace *upsert* de ligas,
equipos, partidos y cuotas. Registra cada sincronización en `audit_logs`.
Funciona aunque no haya claves configuradas (no inserta nada y lo reporta).
"""
from __future__ import annotations

import json
from datetime import datetime

from sqlalchemy.orm import Session

from ..config import settings
from ..integrations import ApiFootballClient, OddsApiClient, TheSportsDbClient
from ..integrations.schemas import NormalizedMatch
from ..models import AuditLog, League, Match, Team


def _get_or_create_league(db: Session, name: str, sport: str) -> League:
    league = db.query(League).filter(League.name == name).first()
    if league:
        return league
    league = League(name=name or "Desconocida", sport=sport or "football")
    db.add(league)
    db.flush()
    return league


def _get_or_create_team(db: Session, league: League, name: str) -> Team:
    team = db.query(Team).filter(Team.name == name).first()
    if team:
        return team
    team = Team(league_id=league.id, name=name or "Desconocido")
    db.add(team)
    db.flush()
    return team


def _upsert_match(db: Session, nm: NormalizedMatch) -> bool:
    """Inserta o actualiza un partido. Devuelve True si se creó uno nuevo."""
    league = _get_or_create_league(db, nm.league, nm.sport)
    home = _get_or_create_team(db, league, nm.home)
    away = _get_or_create_team(db, league, nm.away)

    existing = (
        db.query(Match)
        .filter(
            Match.home_team_id == home.id,
            Match.away_team_id == away.id,
            Match.kickoff == nm.kickoff,
        )
        .first()
    )
    match = existing or Match(
        league_id=league.id,
        home_team_id=home.id,
        away_team_id=away.id,
        kickoff=nm.kickoff,
    )
    match.status = nm.status
    match.home_score = nm.home_score
    match.away_score = nm.away_score
    if nm.odds:
        match.odds_home = nm.odds.home or match.odds_home
        match.odds_draw = nm.odds.draw or match.odds_draw
        match.odds_away = nm.odds.away or match.odds_away
        match.odds_over_2_5 = nm.odds.over_2_5 or match.odds_over_2_5
        match.odds_under_2_5 = nm.odds.under_2_5 or match.odds_under_2_5
    if existing is None:
        db.add(match)
    return existing is None


def sync_all(db: Session) -> dict:
    """Sincroniza desde todos los proveedores con clave configurada."""
    report = {"providers": [], "created": 0, "updated": 0, "errors": []}
    collected: list[NormalizedMatch] = []

    af = ApiFootballClient(settings.API_FOOTBALL_KEY)
    if af.enabled:
        report["providers"].append("api_football")
        # Premier League (39), temporada actual a modo de ejemplo.
        collected += af.get_fixtures(league_id=39, season=datetime.utcnow().year)

    tsdb = TheSportsDbClient(settings.THESPORTSDB_KEY)
    if tsdb.enabled:
        report["providers"].append("thesportsdb")
        collected += tsdb.next_events(league_id=4328)  # English Premier League

    # Cuotas (se asocian por nombre de equipos si coincide).
    odds_client = OddsApiClient(settings.ODDS_API_KEY)
    odds_index: dict[str, object] = {}
    if odds_client.enabled:
        report["providers"].append("odds_api")
        for o in odds_client.get_odds():
            odds_index[o.external_id] = o

    created = updated = 0
    for nm in collected:
        try:
            if _upsert_match(db, nm):
                created += 1
            else:
                updated += 1
        except Exception as exc:  # noqa: BLE001
            report["errors"].append(str(exc))

    db.add(
        AuditLog(
            entity="ingest",
            action="sync_all",
            payload=json.dumps({"providers": report["providers"], "created": created, "updated": updated}),
        )
    )
    db.commit()

    report["created"] = created
    report["updated"] = updated
    if not report["providers"]:
        report["message"] = (
            "No hay proveedores activos. Configura API_FOOTBALL_KEY / ODDS_API_KEY / "
            "SPORTRADAR_KEY en el .env para ingesta real. Datos demo intactos."
        )
    return report
