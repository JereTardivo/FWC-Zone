"""Genera recent_form.json con los ultimos 5 partidos de cada equipo."""
from pathlib import Path
import json
import random

random.seed(42)

ROOT = Path(__file__).parent.parent
DATA_DIR = ROOT / "app" / "data"

with open(DATA_DIR / "teams.json", encoding="utf-8") as f:
    teams = json.load(f)["teams"]

TEAM_IDS = {t["id"] for t in teams}

# Generar forma reciente realista basada en Elo
form = {}

for t in teams:
    tid = t["id"]
    elo = t["elo"]
    matches = []
    for i in range(5):
        # oponente aleatorio de la lista
        opp = random.choice([x for x in teams if x["id"] != tid])
        opp_elo = opp["elo"]
        elo_diff = elo - opp_elo

        # probabilidad de ganar según diferencia de Elo
        win_prob = 1 / (1 + 10 ** (-elo_diff / 400))
        r = random.random()
        if r < win_prob * 0.7:
            result = "W"
        elif r < win_prob * 0.7 + 0.25:
            result = "D"
        else:
            result = "L"

        # goles según diferencia de Elo
        expected_goals = max(0.5, min(3.5, 1.5 + elo_diff / 400 + random.gauss(0, 0.8)))
        conceded = max(0.5, min(3.5, 1.5 - elo_diff / 400 + random.gauss(0, 0.8)))

        gf = max(0, round(expected_goals))
        ga = max(0, round(conceded))

        matches.append({
            "opponent": opp["id"],
            "opponent_name": opp["name"],
            "result": result,
            "goals_for": gf,
            "goals_against": ga,
            "venue": "home" if random.random() > 0.5 else "away",
        })
    form[tid] = {
        "last_5": matches,
        "points": sum({"W": 3, "D": 1, "L": 0}[m["result"]] for m in matches),
        "goals_for": sum(m["goals_for"] for m in matches),
        "goals_against": sum(m["goals_against"] for m in matches),
    }

with open(DATA_DIR / "recent_form.json", "w", encoding="utf-8") as f:
    json.dump({"_meta": {"description": "Forma reciente simulada (ultimos 5 partidos). Cada equipo tiene resultados, goles y oponentes."}, "form": form}, f, ensure_ascii=False, indent=2)

print(f"Generada forma reciente para {len(form)} equipos.")
