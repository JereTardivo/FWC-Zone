"""Parsea Selecciones.txt -> squads.json.

- Mapea nombre de seleccion (espanol) -> id usando teams.json.
- Preserva datos enriquecidos existentes (fifa_rating/market_value/etc.) por jugador,
  matcheando por nombre. No pisa selecciones ya cargadas a mano si --keep las incluye.
- Campos sin dato quedan en null (editables luego).

Uso:
    python scripts/parse_squads.py
"""
from __future__ import annotations

import json
import re
from pathlib import Path

DATA = Path(__file__).resolve().parents[1] / "app" / "data"
TXT = Path(__file__).resolve().parents[2] / "Selecciones.txt"

# Selecciones cuyos datos enriquecidos NO se deben perder (merge por nombre de jugador).
PRESERVE_ENRICHED = {"PAN", "COL"}

SECTIONS = {
    "arqueros": "GK",
    "defensores": "DF",
    "mediocampistas": "MF",
    "volantes": "MF",
    "delanteros": "FW",
}

PLAYER_RE = re.compile(r"([^()]+?)\(([^()]*)\)")


def build_name_index() -> dict[str, str]:
    teams = json.loads((DATA / "teams.json").read_text(encoding="utf-8"))["teams"]
    idx = {t["name"]: t["id"] for t in teams}
    # alias por diferencias de nombre entre el txt y teams.json
    idx["Qatar"] = "QAT"
    idx["República Democrática del Congo"] = "COD"
    return idx


def clean_name(raw: str) -> str:
    name = re.sub(r"^[\s,]*(?:y\s+|e\s+)?", "", raw)
    return name.strip(" ,.\u201c\u201d\"")


def parse_section(body: str, position: str) -> list[dict]:
    players = []
    for m in PLAYER_RE.finditer(body):
        name = clean_name(m.group(1))
        inside = m.group(2).strip()
        if not name:
            continue
        if "," in inside:
            club, cc = inside.rsplit(",", 1)
            club, cc = club.strip(), cc.strip()
        else:
            club, cc = inside.strip(), None
        players.append(
            {
                "name": name,
                "position": position,
                "club": club or None,
                "club_country": cc or None,
                "fifa_rating": None,
                "market_value_eur": None,
                "caps": None,
                "goals": None,
                "age": None,
            }
        )
    return players


def parse_txt(name2id: dict[str, str]) -> dict[str, dict]:
    results: dict[str, dict] = {}
    cur_id = None
    cur_players: list[dict] = []
    cur_coach = None

    def flush():
        nonlocal cur_id, cur_players, cur_coach
        if cur_id and cur_players:
            results[cur_id] = {"coach": cur_coach, "players": cur_players}
        cur_id, cur_players, cur_coach = None, [], None

    for ln in TXT.read_text(encoding="utf-8").splitlines():
        s = ln.strip()
        if not s:
            continue
        low = s.lower()
        key = low.split(":", 1)[0].strip()
        if key in SECTIONS:
            if cur_id and ":" in s:
                cur_players.extend(parse_section(s.split(":", 1)[1], SECTIONS[key]))
            continue
        if low.startswith("dt"):
            cur_coach = s.split(":", 1)[1].strip().rstrip(".") if ":" in s else None
            flush()
            continue
        if low.startswith("faltantes"):
            flush()
            break
        # linea de titulo de seleccion
        flush()
        cur_id = name2id.get(s)  # None si no se mapea (ej. bloque huerfano)
    flush()
    return results


def merge_enriched(old_team: dict, new_team: dict) -> dict:
    """Conserva fifa_rating/market_value/caps/goals/age del viejo por nombre."""
    old_by_name = {p["name"]: p for p in old_team.get("players", [])}
    for p in new_team["players"]:
        o = old_by_name.get(p["name"])
        if not o:
            continue
        for f in ("fifa_rating", "market_value_eur", "caps", "goals", "age"):
            if o.get(f) is not None:
                p[f] = o[f]
    return new_team


def main():
    name2id = build_name_index()
    parsed = parse_txt(name2id)

    squads_path = DATA / "squads.json"
    squads = json.loads(squads_path.read_text(encoding="utf-8"))

    for tid, team in parsed.items():
        if tid in PRESERVE_ENRICHED and tid in squads:
            # mantener exactamente lo cargado a mano (ya enriquecido)
            continue
        squads[tid] = team

    squads_path.write_text(
        json.dumps(squads, ensure_ascii=False, indent=2), encoding="utf-8"
    )

    # reporte
    print("Selecciones parseadas:", len(parsed))
    unmapped = [tid for tid in parsed if tid is None]
    total = 0
    for tid in sorted(k for k in squads if not k.startswith("_")):
        n = len(squads[tid]["players"])
        total += n
        print(f"  {tid}: {n} jugadores | DT: {squads[tid].get('coach')}")
    print("Total jugadores en squads.json:", total)


if __name__ == "__main__":
    main()
