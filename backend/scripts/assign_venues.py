"""Asigna venue_id a todos los fixtures de tournament.json con criterios coherentes."""
from pathlib import Path
import json

ROOT = Path(__file__).parent.parent
DATA_DIR = ROOT / "app" / "data"

with open(DATA_DIR / "tournament.json", encoding="utf-8") as f:
    data = json.load(f)

# Sedes por país para asignar "localidad"
USA = ["nyc", "dal", "atl", "kc", "hou", "la", "sf", "mia", "sea", "phi", "bos"]
CAN = ["van", "tor"]
MEX = ["cdmx", "mty", "gdl"]

# Sedes por rol para fase final
ROLE = {
    "Final": "nyc",
    "Semifinal": ["dal", "atl"],
    "Cuartos": ["kc", "hou", "la", "bos"],
    "Grupos / Octavos": ["sf", "mia", "sea", "phi", "van", "cdmx"],
    "Grupos / Dieciseisavos": ["tor", "mty", "gdl"],
}

# Para fase de grupos: asignar sede según local
# Prioridad: si home es USA/CAN/MEX -> sede de ese país
# Si no, rotar entre todas las sedes de forma geográficamente variada

group_venues = []
# Crear una lista plana de sedes para rotar (ponderadas por capacidad/importancia)
rotation = [
    "nyc", "dal", "atl", "kc", "hou", "la",
    "sf", "mia", "sea", "phi", "bos",
    "van", "tor", "cdmx", "mty", "gdl",
]
# Duplicar las grandes para que aparezcan más
rotation = ["nyc", "dal", "atl", "la", "kc", "hou"] + rotation

venue_idx = 0

def pick_venue(home):
    global venue_idx
    if home in ("USA",):
        v = USA[venue_idx % len(USA)]
    elif home in ("CAN",):
        v = CAN[venue_idx % len(CAN)]
    elif home in ("MEX",):
        v = MEX[venue_idx % len(MEX)]
    else:
        v = rotation[venue_idx % len(rotation)]
    venue_idx += 1
    return v

# Asignar a fase de grupos
for day, matches in data["fixtures"].items():
    for m in matches:
        m["venue_id"] = pick_venue(m["home"])

# Asignar a knockout (usar rol de sede)
knockout = data["knockout"]
# R32 -> sedes de grupos/octavos/dieciseisavos variadas
r32_venues = ["sf", "mia", "sea", "phi", "van", "tor", "cdmx", "mty", "gdl", "la", "hou", "kc", "dal", "atl", "bos", "nyc"]
for i, m in enumerate(knockout.get("R32", [])):
    m["venue_id"] = r32_venues[i % len(r32_venues)]

# R16 -> sedes de octavos/cuartos variadas
r16_venues = ["la", "hou", "kc", "sf", "sea", "phi", "mia", "van"]
for i, m in enumerate(knockout.get("R16", [])):
    m["venue_id"] = r16_venues[i % len(r16_venues)]

# QF -> sedes de cuartos
qf_venues = ["kc", "hou", "la", "bos"]
for i, m in enumerate(knockout.get("QF", [])):
    m["venue_id"] = qf_venues[i % len(qf_venues)]

# SF -> semifinales
sf_venues = ["dal", "atl"]
for i, m in enumerate(knockout.get("SF", [])):
    m["venue_id"] = sf_venues[i % len(sf_venues)]

# THIRD -> Miami (tercer puesto)
for m in knockout.get("THIRD", []):
    m["venue_id"] = "mia"

# FINAL -> NYC
for m in knockout.get("FINAL", []):
    m["venue_id"] = "nyc"

with open(DATA_DIR / "tournament.json", "w", encoding="utf-8") as f:
    json.dump(data, f, ensure_ascii=False, indent=2)

print("Venues asignados a todos los fixtures.")
