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
