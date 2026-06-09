"""Script para traer partidos REALES desde las APIs deportivas.

Uso (con el entorno virtual activado, dentro de la carpeta backend):

    python -m app.sync_data            # añade partidos reales
    python -m app.sync_data --clear    # borra los de ejemplo y pone solo reales

Necesita un archivo backend/.env con tu clave, por ejemplo:

    ODDS_API_KEY=tu_clave_de_the_odds_api

Consíguela gratis en https://the-odds-api.com/
"""
from __future__ import annotations

import sys

from .config import settings
from .database import SessionLocal, init_db
from .services.ingest_service import sync_all


def main() -> None:
    clear = "--clear" in sys.argv

    if not settings.ODDS_API_KEY and not settings.API_FOOTBALL_KEY:
        print("=" * 70)
        print("  ⚠  No se encontró ninguna clave de API.")
        print("  Crea el archivo  backend/.env  con esta línea:")
        print()
        print("      ODDS_API_KEY=tu_clave_de_the_odds_api")
        print()
        print("  Consíguela gratis en https://the-odds-api.com/")
        print("=" * 70)
        return

    init_db()
    db = SessionLocal()
    try:
        print("Sincronizando datos reales… (esto hace 1 llamada por deporte)")
        report = sync_all(db, clear_existing=clear)
    finally:
        db.close()

    print("-" * 70)
    print(f"  Proveedores activos : {', '.join(report.get('providers')) or 'ninguno'}")
    for s in report.get("sports", []):
        print(f"    · {s['sport']}: {s['events']} eventos")
    if "deleted" in report:
        print(f"  Partidos demo borrados : {report['deleted']}")
    print(f"  Partidos nuevos     : {report.get('created', 0)}")
    print(f"  Partidos actualizados: {report.get('updated', 0)}")
    if report.get("errors"):
        print(f"  Avisos              : {len(report['errors'])}")
    if report.get("message"):
        print(f"  Nota: {report['message']}")
    print("-" * 70)
    print("Listo. Recarga http://localhost:3000 con Ctrl+Shift+R para verlos.")


if __name__ == "__main__":
    main()
