# ProTipster AI 📊

> Plataforma profesional de análisis y pronósticos deportivos enfocada en la
> detección de **Value Bets** (apuestas con valor esperado positivo) mediante
> modelos estadísticos, machine learning y gestión profesional de bankroll.

Estética de **terminal de trading financiero**: oscura, densa en datos, verde / negro / blanco.

---

## 1. Visión general

ProTipster AI no "adivina ganadores": estima la **probabilidad real** de cada
resultado con modelos estadísticos (Poisson, Dixon-Coles, ELO, ensembles) y la
compara contra la **probabilidad implícita** de las casas de apuestas. Cuando la
probabilidad estimada supera a la del mercado, existe **edge** (ventaja) y por
tanto una *value bet*. El tamaño de apuesta se calcula con el **criterio de
Kelly** para maximizar el crecimiento del bankroll controlando el riesgo.

```
            ┌──────────────┐     ┌───────────────┐     ┌────────────────┐
 Datos      │  Ingesta de  │     │  Motor de IA  │     │  Detección de  │
 deportivos │   APIs +     │ ──▶ │  (Poisson /   │ ──▶ │  Value Bets    │
 (xG, ELO,  │   features   │     │  Dixon-Coles/ │     │  (edge, EV)    │
 cuotas)    └──────────────┘     │  ELO/Ensemble)│     └───────┬────────┘
                                 └───────────────┘             │
                                                               ▼
                                        ┌──────────────────────────────────┐
                                        │  Bankroll (Kelly) · Ranking de    │
                                        │  picks · Alertas · Backtesting    │
                                        └──────────────────────────────────┘
```

---

## 2. Arquitectura técnica

| Capa            | Tecnología                                            |
|-----------------|-------------------------------------------------------|
| Frontend Web    | Next.js 14 (App Router) · React 18 · TypeScript · Tailwind CSS |
| Móvil           | Expo / React Native (reutiliza la capa `lib/api`)     |
| Backend API     | Python 3.11 · FastAPI · Pydantic v2                    |
| Motor ML        | Núcleo en Python puro (Poisson, Dixon-Coles, ELO, Kelly) + Scikit-learn / XGBoost / LightGBM / TensorFlow para ensembles |
| Base de datos   | PostgreSQL (SQLAlchemy ORM). SQLite para desarrollo   |
| Cache / colas   | Redis                                                 |
| Infra           | Docker · docker-compose · Kubernetes (manifests)      |
| APIs deportivas | API-Football · The Odds API · Sportradar · TheSportsDB |
| Seguridad       | JWT · roles (free / premium / pro / admin) · auditoría |

---

## 3. Estructura de carpetas

```
protipster-ai/
├── README.md                  # este documento (arquitectura + diseño)
├── docker-compose.yml
├── backend/
│   ├── requirements.txt
│   ├── Dockerfile
│   └── app/
│       ├── main.py            # punto de entrada FastAPI
│       ├── config.py          # settings (env)
│       ├── database.py        # sesión SQLAlchemy
│       ├── seed.py            # datos demo
│       ├── core/
│       │   └── security.py    # JWT + hashing + roles
│       ├── ml/                # ⭐ MOTOR DE PREDICCIÓN (Python puro)
│       │   ├── poisson.py
│       │   ├── dixon_coles.py
│       │   ├── elo.py
│       │   ├── value.py       # edge / EV / detección value bet
│       │   ├── kelly.py       # gestión de bankroll
│       │   ├── engine.py      # orquestador (ensemble)
│       │   └── demo.py        # script ejecutable de demostración
│       ├── models/            # tablas SQLAlchemy
│       ├── schemas/           # DTOs Pydantic
│       └── api/routes/        # endpoints REST
└── frontend/
    ├── package.json
    ├── tailwind.config.ts
    ├── app/                   # App Router (dashboard)
    ├── components/            # StatCard, MatchesTable, ValueBets…
    └── lib/                   # cliente API + tipos + mocks
```

---

## 4. Diseño de base de datos

```
users ──< subscriptions           bets >── value_bets >── predictions >── matches
  │                                                                          │
  └──< bankroll_settings           teams ──< matches (home/away)             │
                                   leagues ──< teams                         │
                                   audit_logs (auditoría de pronósticos)  ───┘
```

Tablas principales:

- **users** — `id, email, hashed_password, role(free|premium|pro|admin), created_at`
- **subscriptions** — `id, user_id, plan, status, started_at, expires_at`
- **leagues** — `id, name, sport, country`
- **teams** — `id, league_id, name, elo, xg_for, xg_against`
- **matches** — `id, league_id, home_team_id, away_team_id, kickoff, status, score`
- **predictions** — `id, match_id, market, selection, model_prob, confidence_score, confidence_label, explanation, model_name`
- **value_bets** — `id, prediction_id, bookmaker, odds, implied_prob, model_prob, edge, ev, risk_level, category`
- **bets** — `id, user_id, value_bet_id, stake, status(pending|won|lost), pnl, placed_at`
- **bankroll_settings** — `id, user_id, initial_capital, method(kelly|kelly_fraction|fixed), fraction, max_exposure`
- **audit_logs** — `id, entity, entity_id, action, payload, created_at`

---

## 5. Flujo de usuario

1. **Registro / login** → JWT, rol asignado según plan.
2. **Dashboard** → KPIs (ROI, Yield, Win Rate, beneficio, riesgo), partidos del día, picks destacados.
3. **Detalle de partido** → predicción principal, score de confianza, explicación en lenguaje natural, comparación cuota vs. probabilidad IA.
4. **Value Bets** → lista filtrable por edge / deporte / riesgo, ordenada por ranking de calidad.
5. **Bankroll** → configura capital y método (Kelly / fijo); el sistema sugiere stake por pick y exposición total.
6. **Backtesting** → prueba estrategias sobre histórico (ROI, drawdown, rentabilidad por mercado/deporte).
7. **Alertas** → notificación cuando aparece value bet, se mueve una cuota o hay arbitraje.

---

## 6. Modelos predictivos incluidos

| Modelo        | Uso                                                        | Estado        |
|---------------|------------------------------------------------------------|---------------|
| **Poisson**   | Distribución de goles → probabilidades 1X2 / O-U / BTTS    | ✅ Python puro |
| **Dixon-Coles** | Poisson + corrección de marcadores bajos + ponderación temporal | ✅ Python puro |
| **ELO**       | Fuerza relativa de equipos, ajuste por localía             | ✅ Python puro |
| **Ensemble**  | Combina modelos ponderados                                 | ✅ Python puro |
| Random Forest / XGBoost / LightGBM / NN | Features avanzados (lesiones, fatiga, mercado) | 🧩 hooks listos (requieren librerías ML) |

---

## 7. Puesta en marcha

```bash
# --- Motor ML (sin dependencias, demostrable) ---
python backend/app/ml/demo.py

# --- Backend completo (requiere pip install) ---
cd backend && pip install -r requirements.txt
uvicorn app.main:app --reload          # http://localhost:8000/docs

# --- Frontend ---
cd frontend && npm install && npm run dev   # http://localhost:3000

# --- Todo con Docker ---
docker-compose up --build
```

> ⚠️ **Juego responsable**: ProTipster AI es una herramienta analítica. Ninguna
> apuesta garantiza beneficios; apuesta sólo lo que puedas permitirte perder.
