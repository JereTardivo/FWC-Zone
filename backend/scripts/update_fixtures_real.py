"""Actualiza tournament.json con venue_id y utc_offset reales según Wikipedia."""
from pathlib import Path
import json

ROOT = Path(__file__).parent.parent
DATA_DIR = ROOT / "app" / "data"

with open(DATA_DIR / "tournament.json", encoding="utf-8") as f:
    data = json.load(f)

# Mapa de estadio → venue_id según venues.json
STADIUM_VENUE = {
    "Estadio Azteca": "cdmx",
    "Estadio Chivas": "gdl",  # aka Estadio Akron
    "Estadio BBVA": "mty",
    "BMO Field": "tor",
    "Estadio BC Place": "van",
    "BC Place": "van",
    "MetLife Stadium": "nyc",
    "Gillette Stadium": "bos",
    "Lincoln Financial Field": "phi",
    "Hard Rock Stadium": "mia",
    "Mercedes-Benz Stadium": "atl",
    "SoFi Stadium": "la",
    "Levi's Stadium": "sf",
    "Lumen Field": "sea",
    "AT&T Stadium": "dal",
    "NRG Stadium": "hou",
    "Arrowhead Stadium": "kc",
}

# utc_offset por venue_id (según Wikipedia para junio/julio 2026)
VENUE_OFFSET = {
    "cdmx": -6, "mty": -6, "gdl": -6,
    "dal": -5, "hou": -5, "kc": -5,
    "la": -7, "sf": -7, "sea": -7, "van": -7,
    "nyc": -4, "atl": -4, "bos": -4, "phi": -4, "mia": -4, "tor": -4,
}

# Datos extraídos de Wikipedia para fase de grupos (fecha, home, away) → venue_id
REAL_VENUES = {
    # Fecha 1
    ("2026-06-11", "MEX", "RSA"): "cdmx",
    ("2026-06-11", "KOR", "CZE"): "gdl",
    ("2026-06-12", "CAN", "BIH"): "tor",
    ("2026-06-12", "USA", "PAR"): "la",
    ("2026-06-13", "QAT", "SUI"): "sf",
    ("2026-06-13", "BRA", "MAR"): "nyc",
    ("2026-06-13", "HAI", "SCO"): "bos",
    ("2026-06-14", "AUS", "TUR"): "van",
    ("2026-06-14", "GER", "CUW"): "hou",
    ("2026-06-14", "NED", "JPN"): "dal",
    ("2026-06-14", "CIV", "ECU"): "phi",
    ("2026-06-14", "SWE", "TUN"): "kc",
    ("2026-06-15", "ESP", "CPV"): "atl",
    ("2026-06-15", "BEL", "EGY"): "la",
    ("2026-06-15", "SAU", "URU"): "mia",
    ("2026-06-15", "IRN", "NZL"): "sea",
    ("2026-06-16", "FRA", "SEN"): "nyc",
    ("2026-06-16", "IRQ", "NOR"): "bos",
    ("2026-06-16", "ARG", "ALG"): "kc",
    ("2026-06-17", "AUT", "JOR"): "sf",
    ("2026-06-17", "POR", "COD"): "hou",
    ("2026-06-17", "ENG", "CRO"): "dal",
    ("2026-06-17", "GHA", "PAN"): "tor",
    ("2026-06-17", "UZB", "COL"): "cdmx",

    # Fecha 2
    ("2026-06-18", "CZE", "RSA"): "atl",
    ("2026-06-18", "SUI", "BIH"): "la",
    ("2026-06-18", "CAN", "QAT"): "van",
    ("2026-06-18", "MEX", "KOR"): "cdmx",
    ("2026-06-19", "USA", "AUS"): "sea",
    ("2026-06-19", "SCO", "MAR"): "mia",
    ("2026-06-19", "BRA", "HAI"): "nyc",
    ("2026-06-20", "TUR", "PAR"): "sf",
    ("2026-06-20", "NED", "SWE"): "dal",
    ("2026-06-20", "GER", "CIV"): "hou",
    ("2026-06-20", "ECU", "CUW"): "phi",
    ("2026-06-21", "TUN", "JPN"): "mty",
    ("2026-06-21", "ESP", "SAU"): "atl",
    ("2026-06-21", "BEL", "IRN"): "la",
    ("2026-06-21", "URU", "CPV"): "mia",
    ("2026-06-21", "NZL", "EGY"): "sea",
    ("2026-06-22", "ARG", "AUT"): "dal",
    ("2026-06-22", "FRA", "IRQ"): "bos",
    ("2026-06-22", "NOR", "SEN"): "nyc",
    ("2026-06-23", "JOR", "ALG"): "sf",
    ("2026-06-23", "POR", "UZB"): "hou",
    ("2026-06-23", "ENG", "GHA"): "tor",
    ("2026-06-23", "PAN", "CRO"): "van",
    ("2026-06-23", "COL", "COD"): "gdl",

    # Fecha 3
    ("2026-06-24", "SUI", "CAN"): "van",
    ("2026-06-24", "BIH", "QAT"): "sea",
    ("2026-06-24", "SCO", "BRA"): "nyc",
    ("2026-06-24", "MAR", "HAI"): "mia",
    ("2026-06-24", "RSA", "KOR"): "mty",
    ("2026-06-24", "CZE", "MEX"): "cdmx",
    ("2026-06-25", "ECU", "GER"): "tor",
    ("2026-06-25", "CUW", "CIV"): "phi",
    ("2026-06-25", "TUN", "NED"): "dal",
    ("2026-06-25", "JPN", "SWE"): "hou",
    ("2026-06-25", "PAR", "AUS"): "sf",
    ("2026-06-25", "TUR", "USA"): "la",
    ("2026-06-26", "NOR", "FRA"): "bos",
    ("2026-06-26", "SEN", "IRQ"): "nyc",
    ("2026-06-26", "URU", "ESP"): "gdl",
    ("2026-06-26", "CPV", "SAU"): "atl",
    ("2026-06-27", "EGY", "IRN"): "la",
    ("2026-06-27", "NZL", "BEL"): "sea",
    ("2026-06-27", "CRO", "GHA"): "tor",
    ("2026-06-27", "PAN", "ENG"): "phi",
    ("2026-06-27", "COL", "POR"): "mia",
    ("2026-06-27", "COD", "UZB"): "mty",
    ("2026-06-27", "ALG", "AUT"): "kc",
    ("2026-06-27", "JOR", "ARG"): "dal",
}

updated = 0
for day, matches in data["fixtures"].items():
    for m in matches:
        key = (m["date"], m["home"], m["away"])
        if key in REAL_VENUES:
            vid = REAL_VENUES[key]
            m["venue_id"] = vid
            m["utc_offset"] = VENUE_OFFSET.get(vid, -5)
            updated += 1
        else:
            # mantener venue_id existente pero agregar utc_offset
            vid = m.get("venue_id")
            if vid:
                m["utc_offset"] = VENUE_OFFSET.get(vid, -5)

# También actualizar knockout
for round_name, matches in data.get("knockout", {}).items():
    if not isinstance(matches, list):
        continue
    for m in matches:
        if not isinstance(m, dict):
            continue
        vid = m.get("venue_id")
        if vid:
            m["utc_offset"] = VENUE_OFFSET.get(vid, -5)

with open(DATA_DIR / "tournament.json", "w", encoding="utf-8") as f:
    json.dump(data, f, ensure_ascii=False, indent=2)

print(f"Actualizados {updated} fixtures de fase de grupos con venue_id reales.")
print("Todos los fixtures ahora incluyen utc_offset.")
