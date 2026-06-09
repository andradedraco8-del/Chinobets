"""Servicio de ingesta: vuelca datos de proveedores externos en la BD.

Fuente principal: The Odds API (trae equipos + hora + cuotas en una llamada).
Como The Odds API no aporta estadísticas (xG, ELO), derivamos una estimación de
la fuerza de cada equipo a partir de las cuotas de mercado (probabilidades sin
margen). Así el motor produce predicciones diferenciadas por partido y coherentes
con el mercado, en lugar de salir todas iguales.

Registra cada sincronización en `audit_logs`. Si no hay claves configuradas, no
inserta nada y lo reporta.
"""
from __future__ import annotations

import json
from collections import defaultdict
from datetime import datetime

from sqlalchemy.orm import Session

from ..config import settings
from ..integrations import ApiFootballClient, OddsApiClient, TheSportsDbClient
from ..integrations.schemas import NormalizedMatch
from ..models import AuditLog, League, Match, Team


def _devig_1x2(oh: float | None, od: float | None, oa: float | None) -> tuple[float, float, float] | None:
    """Probabilidades 1X2 sin margen a partir de las cuotas decimales."""
    if not (oh and oa):
        return None
    ih = 1.0 / oh
    ia = 1.0 / oa
    idr = 1.0 / od if od else 0.0
    total = ih + idr + ia
    if total <= 0:
        return None
    return ih / total, idr / total, ia / total


def _strength_to_stats(strength: float) -> dict:
    """Mapea una 'fuerza de mercado' (0-1) a ratings utilizables por el motor."""
    s = max(0.05, min(0.95, strength))
    elo = 1500 + (s - 0.45) * 520
    xg_for = max(0.5, min(3.0, 0.7 + s * 1.9))
    xg_against = max(0.5, min(2.5, 2.0 - s * 1.4))
    return {
        "elo": round(elo, 1),
        "xg_for": round(xg_for, 2),
        "xg_against": round(xg_against, 2),
        "attack": round(xg_for / 1.4, 3),
        "defense": round(xg_against / 1.4, 3),
    }


def _get_or_create_league(db: Session, name: str, sport: str) -> League:
    league = db.query(League).filter(League.name == name).first()
    if league:
        return league
    league = League(name=name or "Desconocida", sport=sport or "football")
    db.add(league)
    db.flush()
    return league


def _get_or_create_team(db: Session, league: League, name: str, stats: dict | None) -> Team:
    team = db.query(Team).filter(Team.name == name).first()
    if not team:
        team = Team(league_id=league.id, name=name or "Desconocido")
        db.add(team)
        db.flush()
    if stats:
        team.elo = stats["elo"]
        team.xg_for = stats["xg_for"]
        team.xg_against = stats["xg_against"]
        team.attack = stats["attack"]
        team.defense = stats["defense"]
    return team


def _compute_team_strengths(matches: list[NormalizedMatch]) -> dict[str, float]:
    """Fuerza media de cada equipo según la prob. de ganar implícita del mercado."""
    acc: dict[str, list[float]] = defaultdict(list)
    for nm in matches:
        if not nm.odds:
            continue
        probs = _devig_1x2(nm.odds.home, nm.odds.draw, nm.odds.away)
        if not probs:
            continue
        p_home, _, p_away = probs
        # Descontamos parte de la ventaja de localía para no inflar al local.
        acc[nm.home].append(max(0.0, p_home - 0.06))
        acc[nm.away].append(min(1.0, p_away + 0.06))
    return {team: (sum(v) / len(v)) for team, v in acc.items() if v}


def _upsert_match(db: Session, nm: NormalizedMatch, strengths: dict[str, float]) -> bool:
    league = _get_or_create_league(db, nm.league, nm.sport)
    home = _get_or_create_team(db, league, nm.home, _stats_for(nm.home, strengths))
    away = _get_or_create_team(db, league, nm.away, _stats_for(nm.away, strengths))

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


def _stats_for(team_name: str, strengths: dict[str, float]) -> dict | None:
    s = strengths.get(team_name)
    return _strength_to_stats(s) if s is not None else None


def sync_all(db: Session, clear_existing: bool = False, sports: list[str] | None = None) -> dict:
    """
    Sincroniza desde los proveedores con clave configurada.

    `clear_existing`: si True, elimina los partidos actuales (p. ej. los de
    demostración) antes de insertar los reales.
    `sports`: lista de 'sport_key' de The Odds API a sincronizar; si es None,
    usa la lista por defecto de la configuración.
    """
    report: dict = {"providers": [], "created": 0, "updated": 0, "errors": [], "sports": []}
    collected: list[NormalizedMatch] = []
    sport_keys = sports or settings.ODDS_API_SPORTS

    # --- The Odds API (principal: equipos + cuotas) ---
    odds_client = OddsApiClient(settings.ODDS_API_KEY)
    if odds_client.enabled:
        report["providers"].append("odds_api")
        for sport_key in sport_keys:
            found = odds_client.get_matches(sport_key=sport_key, regions=settings.ODDS_API_REGIONS)
            report["sports"].append({"sport": sport_key, "events": len(found)})
            collected += found

    # --- API-Football (opcional, fixtures con marcador) ---
    af = ApiFootballClient(settings.API_FOOTBALL_KEY)
    if af.enabled:
        report["providers"].append("api_football")
        collected += af.get_fixtures(league_id=39, season=datetime.utcnow().year)

    # --- TheSportsDB (opcional, catálogo gratuito) ---
    tsdb = TheSportsDbClient(settings.THESPORTSDB_KEY)
    if tsdb.enabled and settings.ODDS_API_KEY == "":
        # Sólo como respaldo si no hay The Odds API (evita partidos sin cuotas).
        report["providers"].append("thesportsdb")
        collected += tsdb.next_events(league_id=4328)

    if not report["providers"]:
        report["message"] = (
            "No hay proveedores activos. Crea backend/.env con ODDS_API_KEY=tu_clave "
            "para traer partidos reales. Datos demo intactos."
        )
        return report

    if clear_existing:
        deleted = db.query(Match).delete()
        report["deleted"] = deleted

    strengths = _compute_team_strengths(collected)

    created = updated = 0
    for nm in collected:
        if not nm.home or not nm.away:
            continue
        try:
            if _upsert_match(db, nm, strengths):
                created += 1
            else:
                updated += 1
        except Exception as exc:  # noqa: BLE001
            report["errors"].append(str(exc))

    db.add(AuditLog(
        entity="ingest",
        action="sync_all",
        payload=json.dumps({"providers": report["providers"], "created": created, "updated": updated}),
    ))
    db.commit()

    report["created"] = created
    report["updated"] = updated
    return report
