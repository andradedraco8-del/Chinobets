"""Cliente HTTP base para los proveedores deportivos."""
from __future__ import annotations

import logging
from typing import Any

try:
    import httpx
except ImportError:  # httpx es dependencia opcional en entornos sin red
    httpx = None  # type: ignore

logger = logging.getLogger("protipster.integrations")


class BaseProviderClient:
    """Encapsula peticiones GET con cabeceras, timeout y manejo de errores."""

    base_url: str = ""

    def __init__(self, api_key: str = "", timeout: float = 10.0) -> None:
        self.api_key = api_key
        self.timeout = timeout

    @property
    def enabled(self) -> bool:
        """El cliente está operativo si hay clave y httpx disponible."""
        return bool(self.api_key) and httpx is not None

    def _headers(self) -> dict[str, str]:
        return {}

    def _get(self, path: str, params: dict | None = None) -> dict[str, Any] | None:
        """GET resiliente: devuelve None ante cualquier fallo (no rompe la app)."""
        if httpx is None:
            logger.warning("httpx no instalado; integración deshabilitada")
            return None
        url = f"{self.base_url}{path}"
        try:
            with httpx.Client(timeout=self.timeout) as client:
                resp = client.get(url, params=params or {}, headers=self._headers())
                resp.raise_for_status()
                return resp.json()
        except Exception as exc:  # noqa: BLE001
            logger.warning("Fallo al consultar %s: %s", url, exc)
            return None
