"""Integraciones con proveedores de datos deportivos.

Cada cliente expone una interfaz uniforme y degrada con elegancia cuando no hay
clave de API configurada o no hay conectividad (devuelve listas vacías en lugar
de lanzar excepciones), de modo que la aplicación sigue siendo usable con los
datos sembrados.
"""
from .api_football import ApiFootballClient
from .odds_api import OddsApiClient
from .sportradar import SportradarClient
from .thesportsdb import TheSportsDbClient

__all__ = [
    "ApiFootballClient",
    "OddsApiClient",
    "SportradarClient",
    "TheSportsDbClient",
]
