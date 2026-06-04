"""Carga y cachea los datos de equipos y del torneo desde JSON."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Dict, List

from .engine.probability import TeamStrength

DATA_DIR = Path(__file__).parent / "data"


def load_raw_teams() -> List[dict]:
    with open(DATA_DIR / "teams.json", encoding="utf-8") as f:
        return json.load(f)["teams"]


def load_tournament() -> dict:
    with open(DATA_DIR / "tournament.json", encoding="utf-8") as f:
        return json.load(f)


def load_squads() -> dict:
    path = DATA_DIR / "squads.json"
    if not path.exists():
        return {}
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def load_venues() -> List[dict]:
    path = DATA_DIR / "venues.json"
    if not path.exists():
        return []
    with open(path, encoding="utf-8") as f:
        return json.load(f).get("venues", [])


def load_recent_form() -> dict:
    path = DATA_DIR / "recent_form.json"
    if not path.exists():
        return {}
    with open(path, encoding="utf-8") as f:
        return json.load(f).get("form", {})


def form_factor(team_id: str) -> float:
    """Factor de forma reciente: puntos de ultimos 5 partidos normalizados.
    15 puntos = +1.0 (maximo), 0 puntos = -1.5 (minimo).
    """
    form = load_recent_form().get(team_id, {})
    pts = form.get("points", 7)
    # 7.5 es el promedio esperado (1.5 por partido), scale para que tenga impacto moderado
    return (pts - 7.5) / 7.5


def squad_market_value(team_id: str) -> float:
    """Valor de mercado total del plantel en millones de euros.
    Si no hay datos, devuelve 0.
    """
    squads = load_squads()
    squad = squads.get(team_id, {})
    players = squad.get("players", [])
    if not players:
        return 0.0
    total = 0.0
    for p in players:
        val = p.get("market_value_millions")
        if val is not None:
            total += float(val)
    return total


def avg_market_value() -> float:
    """Promedio de valor de mercado entre todos los equipos con datos."""
    teams = load_raw_teams()
    values = [squad_market_value(t["id"]) for t in teams if squad_market_value(t["id"]) > 0]
    return sum(values) / len(values) if values else 1.0


def build_team_index() -> Dict[str, dict]:
    return {t["id"]: t for t in load_raw_teams()}


def team_strength(raw: dict) -> TeamStrength:
    return TeamStrength(
        id=raw["id"],
        name=raw["name"],
        elo=float(raw["elo"]),
        attack=float(raw["attack"]),
        defense=float(raw["defense"]),
    )


def strength_index() -> Dict[str, TeamStrength]:
    return {t["id"]: team_strength(t) for t in load_raw_teams()}
