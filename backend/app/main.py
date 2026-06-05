"""API FastAPI - Tactiqo Mundial 2026."""
from __future__ import annotations

from typing import List, Optional

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from .data_loader import (
    build_team_index, load_squads, load_tournament, load_venues,
    load_recent_form, strength_index, form_factor, squad_market_value, avg_market_value,
)
from .engine.probability import predict_match
from .engine.ml_predictor import MLPredictor
from .simulator import TournamentSimulator

app = FastAPI(
    title="Tactiqo Mundial 2026",
    description="Motor estadistico (Elo + Poisson + Monte Carlo) para estimar resultados del Mundial 2026.",
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


# ----------------------------- Schemas -----------------------------
class Team(BaseModel):
    id: str
    name: str
    confederation: str
    elo: float
    attack: float
    defense: float
    fifa_rank: Optional[int] = None
    host: Optional[bool] = False


class MatchRequest(BaseModel):
    home: str
    away: str
    neutral: bool = True


# ----------------------------- Endpoints -----------------------------
@app.get("/api/health")
def health():
    return {"status": "ok"}


@app.get("/api/venues")
def get_venues():
    return load_venues()


@app.get("/api/teams", response_model=List[Team])
def get_teams():
    return list(build_team_index().values())


@app.get("/api/tournament")
def get_tournament():
    data = load_tournament()
    idx = build_team_index()
    groups = {
        gid: [idx[tid] for tid in teams if tid in idx]
        for gid, teams in data["groups"].items()
    }
    return {
        "meta": data["_meta"],
        "groups": groups,
        "pots": data.get("pots", {}),
        "knockout": data.get("knockout", {}),
    }


@app.get("/api/team/{team_id}")
def get_team(team_id: str):
    idx = build_team_index()
    if team_id not in idx:
        raise HTTPException(status_code=404, detail="Equipo no encontrado")
    raw = idx[team_id]
    squads = load_squads()
    squad = squads.get(team_id)

    # grupo al que pertenece
    data = load_tournament()
    group = next((g for g, members in data["groups"].items() if team_id in members), None)

    # forma reciente
    recent = load_recent_form().get(team_id, {})

    # valor de mercado
    mv = squad_market_value(team_id)

    return {
        "team": raw,
        "group": group,
        "has_squad": squad is not None,
        "coach": (squad or {}).get("coach"),
        "players": (squad or {}).get("players", []),
        "recent_form": recent,
        "market_value_millions": round(mv, 1) if mv > 0 else None,
    }


@app.get("/api/form")
def get_form():
    return load_recent_form()


@app.get("/api/fixtures")
def get_fixtures(matchday: Optional[str] = None, with_prediction: bool = True):
    data = load_tournament()
    idx = build_team_index()
    strengths = strength_index()
    fixtures = data.get("fixtures", {})
    days = [matchday] if matchday else sorted(fixtures.keys())

    venues = {v["id"]: v for v in load_venues()}
    avg_mv = avg_market_value()

    out = {}
    for d in days:
        matches = []
        for m in fixtures.get(d, []):
            h, a = m["home"], m["away"]
            entry = {
                "group": m.get("group"),
                "date": m.get("date"),
                "time": m.get("time"),
                "utc_offset": m.get("utc_offset"),
                "home": {"id": h, "name": idx.get(h, {}).get("name", h)},
                "away": {"id": a, "name": idx.get(a, {}).get("name", a)},
            }
            vid = m.get("venue_id")
            if vid and vid in venues:
                v = venues[vid]
                entry["venue"] = {
                    "id": vid,
                    "stadium": v["stadium"],
                    "city": v["city"],
                    "country": v["country"],
                }
            if with_prediction and h in strengths and a in strengths:
                p = predict_match(
                    strengths[h], strengths[a], neutral=True,
                    home_form=form_factor(h), away_form=form_factor(a),
                    home_market=max(0.5, squad_market_value(h) / avg_mv) if squad_market_value(h) > 0 else 1.0,
                    away_market=max(0.5, squad_market_value(a) / avg_mv) if squad_market_value(a) > 0 else 1.0,
                )
                entry["prediction"] = {
                    "prob_home": p.prob_home,
                    "prob_draw": p.prob_draw,
                    "prob_away": p.prob_away,
                    "expected_home_goals": p.expected_home_goals,
                    "expected_away_goals": p.expected_away_goals,
                    "over_2_5": p.over_2_5,
                    "btts": p.btts,
                    "top_scorelines": p.top_scorelines,
                }
            matches.append(entry)
        out[d] = matches
    return {"matchdays": out}


@app.post("/api/predict")
def predict(req: MatchRequest):
    strengths = strength_index()
    if req.home not in strengths or req.away not in strengths:
        raise HTTPException(status_code=404, detail="Equipo no encontrado")
    avg_mv = avg_market_value()
    pred = predict_match(
        strengths[req.home], strengths[req.away], neutral=req.neutral,
        home_form=form_factor(req.home), away_form=form_factor(req.away),
        home_market=max(0.5, squad_market_value(req.home) / avg_mv) if squad_market_value(req.home) > 0 else 1.0,
        away_market=max(0.5, squad_market_value(req.away) / avg_mv) if squad_market_value(req.away) > 0 else 1.0,
    )
    return pred.__dict__


@app.post("/api/predict-ml")
def predict_ml(req: MatchRequest):
    """Prediccion alternativa via Gradient Boosting (entrenado sobre Mundiales 1998-2022)."""
    ml = MLPredictor()
    if not ml.is_ready():
        raise HTTPException(status_code=503, detail="Modelo ML no disponible. Ejecutar: python -m backend.scripts.train_ml_model")
    result = ml.predict(req.home, req.away, neutral=req.neutral)
    if result is None:
        raise HTTPException(status_code=404, detail="Equipo no encontrado")
    return result


@app.get("/api/simulate")
def simulate(
    iterations: int = Query(5000, ge=100, le=100000),
    seed: Optional[int] = None,
):
    data = load_tournament()
    sim = TournamentSimulator(strength_index(), data["groups"])
    result = sim.run(iterations=iterations, seed=seed)
    idx = build_team_index()
    for t in result["teams"]:
        raw = idx.get(t["team_id"], {})
        t["name"] = raw.get("name", t["team_id"])
        t["confederation"] = raw.get("confederation", "")
    return result
