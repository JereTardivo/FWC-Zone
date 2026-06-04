"""Actualiza teams.json con rankings FIFA reales (junio 2026) y ajusta Elo/attack/defense."""
from pathlib import Path
import json

ROOT = Path(__file__).parent.parent
DATA_DIR = ROOT / "app" / "data"

with open(DATA_DIR / "teams.json", encoding="utf-8") as f:
    data = json.load(f)

# Rankings FIFA reales según USA Today (junio 2026)
FIFA_RANKS = {
    "FRA": 1, "ESP": 2, "ARG": 3, "ENG": 4, "POR": 5,
    "BRA": 6, "MAR": 7, "NED": 8, "BEL": 9, "GER": 10,
    "CRO": 11, "COL": 13, "SEN": 14, "MEX": 15, "USA": 16,
    "URU": 17, "JPN": 18, "SUI": 19, "IRN": 21, "TUR": 22,
    "AUT": 23, "ECU": 24, "KOR": 25, "AUS": 27, "ALG": 28,
    "EGY": 29, "CAN": 30, "NOR": 31, "PAN": 33, "CIV": 34,
    "SWE": 38, "PAR": 40, "CZE": 41, "SCO": 43, "COD": 45,
    "TUN": 46, "UZB": 50, "QAT": 55, "IRQ": 57, "RSA": 60,
    "SAU": 61, "JOR": 63, "BIH": 64, "CPV": 68, "GHA": 73,
    "HAI": 82, "CUW": 83, "NZL": 85,
}

# Ajustar attack/defense según ranking FIFA (más alto = mejor)
def adjust_strength(team):
    rank = team.get("fifa_rank", 50)
    # Base attack/defense escalados inversamente al ranking
    # Top 10: attack 1.9-2.1, defense 0.85-1.0
    # 11-20: attack 1.7-1.9, defense 0.95-1.05
    # 21-35: attack 1.5-1.7, defense 1.0-1.1
    # 36-50: attack 1.3-1.5, defense 1.05-1.15
    # 50+: attack 1.1-1.3, defense 1.1-1.25
    if rank <= 10:
        attack = 2.1 - (rank - 1) * 0.02
        defense = 0.85 + (rank - 1) * 0.015
    elif rank <= 20:
        attack = 1.9 - (rank - 11) * 0.02
        defense = 0.95 + (rank - 11) * 0.01
    elif rank <= 35:
        attack = 1.7 - (rank - 21) * 0.013
        defense = 1.0 + (rank - 21) * 0.007
    elif rank <= 50:
        attack = 1.5 - (rank - 36) * 0.013
        defense = 1.05 + (rank - 36) * 0.007
    else:
        attack = 1.3 - (rank - 51) * 0.005
        defense = 1.15 + (rank - 51) * 0.003

    # Ajustar Elo: correlación aproximada con ranking FIFA
    # Top 3 ≈ 2100+, top 10 ≈ 1950-2080, top 20 ≈ 1850-1950, etc.
    if rank <= 3:
        elo = 2120 - (rank - 1) * 20
    elif rank <= 10:
        elo = 2080 - (rank - 4) * 18
    elif rank <= 20:
        elo = 1970 - (rank - 11) * 12
    elif rank <= 30:
        elo = 1860 - (rank - 21) * 10
    elif rank <= 40:
        elo = 1770 - (rank - 31) * 9
    elif rank <= 50:
        elo = 1690 - (rank - 41) * 8
    else:
        elo = 1610 - (rank - 51) * 5

    team["elo"] = round(elo)
    team["attack"] = round(attack, 2)
    team["defense"] = round(defense, 2)
    team["fifa_rank"] = rank


updated = 0
for team in data["teams"]:
    tid = team["id"]
    if tid in FIFA_RANKS:
        old_rank = team.get("fifa_rank")
        new_rank = FIFA_RANKS[tid]
        adjust_strength(team)
        updated += 1
        print(f"{tid}: FIFA {old_rank} -> {new_rank}, Elo {team['elo']}, atk {team['attack']}, def {team['defense']}")

with open(DATA_DIR / "teams.json", "w", encoding="utf-8") as f:
    json.dump(data, f, ensure_ascii=False, indent=2)

print(f"\nActualizados {updated} equipos.")
