"""Script para traer partidos REALES desde las APIs deportivas.

Uso (con el entorno virtual activado, dentro de la carpeta backend):

    python -m app.sync_data --list                  # ver competiciones activas
    python -m app.sync_data                          # sincroniza las ligas por defecto
    python -m app.sync_data --clear                  # borra las de ejemplo y pone solo reales
    python -m app.sync_data --clear soccer_fifa_world_cup   # elige competiciones a mano

Puedes poner varias competiciones separadas por espacios. Para saber cuáles
existen ahora mismo, usa --list y copia los 'key' que te interesen.

Necesita backend/.env con tu clave:  ODDS_API_KEY=tu_clave
Consíguela gratis en https://the-odds-api.com/
"""
from __future__ import annotations

import sys

from .config import settings
from .database import SessionLocal, init_db
from .integrations import OddsApiClient
from .services.ingest_service import sync_all


def _print_sports() -> None:
    client = OddsApiClient(settings.ODDS_API_KEY)
    sports = client.list_sports()
    if not sports:
        print("No se pudieron obtener las competiciones (¿clave correcta?).")
        return
    print("=" * 72)
    print("  COMPETICIONES ACTIVAS AHORA MISMO (copia el 'key' que quieras):")
    print("=" * 72)
    grupo_actual = None
    for s in sorted(sports, key=lambda x: (x.get("group") or "", x.get("key") or "")):
        if s.get("group") != grupo_actual:
            grupo_actual = s.get("group")
            print(f"\n  ── {grupo_actual} ──")
        print(f"    {s['key']:<42} {s['title']}")
    print()
    print("  Ejemplo:  python -m app.sync_data --clear soccer_fifa_world_cup")
    print("=" * 72)


def main() -> None:
    args = sys.argv[1:]
    clear = "--clear" in args
    list_only = "--list" in args
    # Cualquier argumento que no empiece por '--' es una competición elegida.
    chosen = [a for a in args if not a.startswith("--")]

    if not settings.ODDS_API_KEY and not settings.API_FOOTBALL_KEY:
        print("=" * 70)
        print("  ⚠  No se encontró ninguna clave de API.")
        print("  Crea el archivo  backend/.env  con esta línea:")
        print("      ODDS_API_KEY=tu_clave_de_the_odds_api")
        print("  Consíguela gratis en https://the-odds-api.com/")
        print("=" * 70)
        return

    if list_only:
        _print_sports()
        return

    init_db()
    db = SessionLocal()
    try:
        print("Sincronizando datos reales… (1 llamada por competición)")
        report = sync_all(db, clear_existing=clear, sports=chosen or None)
    finally:
        db.close()

    print("-" * 70)
    print(f"  Proveedores activos : {', '.join(report.get('providers')) or 'ninguno'}")
    for s in report.get("sports", []):
        marca = "✓" if s["events"] else "·"
        print(f"    {marca} {s['sport']}: {s['events']} eventos")
    if "deleted" in report:
        print(f"  Partidos demo borrados : {report['deleted']}")
    print(f"  Partidos nuevos     : {report.get('created', 0)}")
    print(f"  Partidos actualizados: {report.get('updated', 0)}")
    if report.get("message"):
        print(f"  Nota: {report['message']}")
    print("-" * 70)
    print("Listo. Recarga http://localhost:3000 con Ctrl+Shift+R para verlos.")


if __name__ == "__main__":
    main()
