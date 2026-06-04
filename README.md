# Tactiqo ⚽

> **Tactiqo** — del inglés *tactics* + *IQ*. Inteligencia táctica aplicada al fútbol.
>
> Motor estadístico para estimar resultados del FIFA World Cup 2026.

Web app para estimar resultados del **FIFA World Cup 2026** (48 equipos, 12 grupos)
con un motor **estadístico y probabilístico**:

- **Elo** → fuerza relativa de cada selección y probabilidad 1X2.
- **Modelo Poisson** → distribución de goles, marcadores exactos, over/under, ambos marcan.
- **Simulación Monte Carlo** → juega el torneo completo miles de veces y calcula
  probabilidad de campeón, de avanzar de fase y de ganar el grupo.

> Los datos (`ratings` de equipos y el sorteo de grupos) son **seed editables**.
> Reemplazalos con datos reales cuando se confirme el sorteo (diciembre 2025).

## Arquitectura

```
PrediccionMundial/
├─ backend/                 # API FastAPI + motor estadístico (Python)
│  ├─ app/
│  │  ├─ data/              # teams.json, tournament.json  (EDITABLES)
│  │  ├─ engine/            # probability.py  (Elo + Poisson)
│  │  ├─ simulator.py       # Monte Carlo del torneo
│  │  ├─ data_loader.py
│  │  └─ main.py            # endpoints REST
│  └─ requirements.txt
└─ frontend/                # React + Vite + Tailwind
   └─ src/
      ├─ components/        # Groups, MatchPredictor, Simulation
      ├─ api.js
      └─ App.jsx
```

## Cómo correrlo

### 1) Backend (Python 3.10+)

```powershell
cd backend
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

API en `http://localhost:8000` · docs interactivas en `http://localhost:8000/docs`

### 2) Frontend

```powershell
cd frontend
npm install
npm run dev
```

App en `http://localhost:5173` (el proxy de Vite redirige `/api` al backend).

## Endpoints

| Método | Ruta | Descripción |
|--------|------|-------------|
| GET | `/api/teams` | Lista de equipos con ratings |
| GET | `/api/tournament` | Grupos y bombos |
| POST | `/api/predict` | Predice un partido `{home, away, neutral}` |
| GET | `/api/simulate?iterations=5000` | Simula el torneo completo |

## El motor estadístico (resumen)

Para cada partido se calculan los **goles esperados** (λ) de cada equipo
combinando ataque/defensa y la diferencia de Elo:

```
λ_local = ataque_local · (defensa_visita / defensa_liga) · e^(k·ΔElo)
λ_visita = ataque_visita · (defensa_local / defensa_liga) · e^(-k·ΔElo)
```

Con esos λ se arma la **matriz de marcadores Poisson** y de ahí salen todas las
probabilidades (1X2, over/under, BTTS, marcadores exactos). La simulación
Monte Carlo muestrea goles partido a partido a lo largo de todo el cuadro.

## Próximos pasos (ideas para hacerlo "ultrapotente")

### ✅ Realizado

- [x] Cargar ratings reales (FIFA/Elo) y actualizar tras cada fecha.
- [x] Factores externos: forma reciente (últimos 5 partidos), valor de mercado del plantel, sedes con altitud/clima y zonas horarias.
- [x] Modelo Poisson bivariado con correlación (Dixon-Coles) para marcadores bajos.

### 🔄 Pendiente

- [ ] Calibración con históricos de Mundiales (backtesting + Brier score).
- [ ] Persistencia (SQLite/Postgres) y actualización de resultados en vivo.
- [ ] Modelo ML (gradient boosting) sobre features de equipos como alternativa al Elo.
```
