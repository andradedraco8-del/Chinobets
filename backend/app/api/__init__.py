"""Agrega todos los routers de la API bajo /api."""
from fastapi import APIRouter

from .routes import auth, bankroll, dashboard, matches, predictions, value_bets

api_router = APIRouter(prefix="/api")
api_router.include_router(auth.router)
api_router.include_router(dashboard.router)
api_router.include_router(matches.router)
api_router.include_router(predictions.router)
api_router.include_router(value_bets.router)
api_router.include_router(bankroll.router)
