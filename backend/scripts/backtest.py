"""Backtesting del modelo Tactiqo contra resultados históricos de Mundiales.

Fuentes de datos:
- Partidos: Fjelstul World Cup Database (jfjelstul/worldcup)
- Ratings Elo: JGravier/soccer-elo (eloratings.net)
- Attack/Defense: teams.json actual (aproximación)

Uso:
    cd backend
    python -m scripts.backtest
"""

import csv
import json
import sys
from pathlib import Path
from statistics import mean

# Add parent to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.engine.probability import TeamStrength, predict_match

# -- Config --
DATA_DIR = Path(__file__).parent.parent / "app" / "data"
MUNDIALES = [2014, 2018, 2022]

# Mapeo: nombre en español (teams.json) -> nombre en inglés (datasets)
NAME_MAP = {
    "Argentina": "Argentina",
    "Francia": "France",
    "España": "Spain",
    "Inglaterra": "England",
    "Brasil": "Brazil",
    "Portugal": "Portugal",
    "Países Bajos": "Netherlands",
    "Bélgica": "Belgium",
    "Alemania": "Germany",
    "Croacia": "Croatia",
    "Uruguay": "Uruguay",
    "Colombia": "Colombia",
    "Marruecos": "Morocco",
    "Estados Unidos": "United States",
    "México": "Mexico",
    "Suiza": "Switzerland",
    "Japón": "Japan",
    "Senegal": "Senegal",
    "Austria": "Austria",
    "Corea del Sur": "South Korea",
    "Ecuador": "Ecuador",
    "Canadá": "Canada",
    "Australia": "Australia",
    "Egipto": "Egypt",
    "Costa de Marfil": "Ivory Coast",
    "Irán": "Iran",
    "Túnez": "Tunisia",
    "Paraguay": "Paraguay",
    "Escocia": "Scotland",
    "Noruega": "Norway",
    "Catar": "Qatar",
    "Arabia Saudita": "Saudi Arabia",
    "Ghana": "Ghana",
    "Panamá": "Panama",
    "Argelia": "Algeria",
    "Uzbekistán": "Uzbekistan",
    "Jordania": "Jordan",
    "Sudáfrica": "South Africa",
    "Cabo Verde": "Cape Verde",
    "Nueva Zelanda": "New Zealand",
    "República Checa": "Czechia",
    "Suecia": "Sweden",
    "Turquía": "Turkey",
    "RD Congo": "DR Congo",
    "Bosnia y Herzegovina": "Bosnia and Herzegovina",
    "Irak": "Iraq",
    "Haití": "Haiti",
    "Curazao": "Curaçao",
    "Guatemala": "Guatemala",
    "Honduras": "Honduras",
    "Jamaica": "Jamaica",
    "Costa Rica": "Costa Rica",
    "El Salvador": "El Salvador",
    "Nicaragua": "Nicaragua",
    "Bolivia": "Bolivia",
    "Chile": "Chile",
    "Perú": "Peru",
    "Venezuela": "Venezuela",
    "Polonia": "Poland",
    "Dinamarca": "Denmark",
    "Italia": "Italy",
    "Gales": "Wales",
    "Ucrania": "Ukraine",
    "Serbia": "Serbia",
    "Grecia": "Greece",
    "Rusia": "Russia",
    "Eslovaquia": "Slovakia",
    "Eslovenia": "Slovenia",
    "Islandia": "Iceland",
    "Nigeria": "Nigeria",
    "Camerún": "Cameroon",
    "Costa de Marfil": "Ivory Coast",
    "Egipto": "Egypt",
    "Marruecos": "Morocco",
    "Túnez": "Tunisia",
    "Ghana": "Ghana",
    "Senegal": "Senegal",
    "Argelia": "Algeria",
    "Nigeria": "Nigeria",
    "Costa Rica": "Costa Rica",
    "Honduras": "Honduras",
    "Panamá": "Panama",
    "Jamaica": "Jamaica",
    "México": "Mexico",
    "Estados Unidos": "United States",
    "Canadá": "Canada",
    "Japón": "Japan",
    "Corea del Sur": "South Korea",
    "Australia": "Australia",
    "Irán": "Iran",
    "Arabia Saudita": "Saudi Arabia",
    "Catar": "Qatar",
    "China": "China",
    "Uzbekistán": "Uzbekistan",
    "Jordania": "Jordan",
    "Irak": "Iraq",
    "Siria": "Syria",
    "Líbano": "Lebanon",
    "Kuwait": "Kuwait",
    "Emiratos Árabes Unidos": "United Arab Emirates",
    "Omán": "Oman",
    "Bahréin": "Bahrain",
    "Tailandia": "Thailand",
    "Vietnam": "Vietnam",
    "Malasia": "Malaysia",
    "Indonesia": "Indonesia",
    "Filipinas": "Philippines",
    "Singapur": "Singapore",
    "Myanmar": "Myanmar",
    "Camboya": "Cambodia",
    "Laos": "Laos",
    "Brunéi": "Brunei",
    "Timor Oriental": "East Timor",
    "India": "India",
    "Pakistán": "Pakistan",
    "Bangladesh": "Bangladesh",
    "Afganistán": "Afghanistan",
    "Nepal": "Nepal",
    "Bután": "Bhutan",
    "Maldivas": "Maldives",
    "Sri Lanka": "Sri Lanka",
    "Kirguistán": "Kyrgyzstan",
    "Tayikistán": "Tajikistan",
    "Turkmenistán": "Turkmenistan",
    "Kazajistán": "Kazakhstan",
    "Mongolia": "Mongolia",
    "Corea del Norte": "North Korea",
    "China Taipéi": "Chinese Taipei",
    "Hong Kong": "Hong Kong",
    "Macao": "Macau",
    "Guam": "Guam",
    "Islas Marianas del Norte": "Northern Mariana Islands",
    "Samoa Estadounidense": "American Samoa",
    "Samoa": "Samoa",
    "Tonga": "Tonga",
    "Fiyi": "Fiji",
    "Vanuatu": "Vanuatu",
    "Nueva Caledonia": "New Caledonia",
    "Islas Salomón": "Solomon Islands",
    "Papúa Nueva Guinea": "Papua New Guinea",
    "Islas Cook": "Cook Islands",
    "Tahití": "Tahiti",
    "Kiribati": "Kiribati",
    "Tuvalu": "Tuvalu",
    "Nauru": "Nauru",
    "Palaos": "Palau",
    "Islas Marshall": "Marshall Islands",
    "Micronesia": "Micronesia",
}

# Invertir para lookup rápido
EN_TO_ES = {v: k for k, v in NAME_MAP.items()}


def load_teams():
    """Carga teams.json y devuelve dict id -> dict con attack/defense."""
    with open(DATA_DIR / "teams.json", "r", encoding="utf-8") as f:
        data = json.load(f)
    by_name = {}
    for t in data["teams"]:
        by_name[t["name"]] = {
            "id": t["id"],
            "attack": t["attack"],
            "defense": t["defense"],
            "elo": t["elo"],
        }
    return by_name


def load_elo_history():
    """Carga ratings Elo históricos: {(año, nombre_en): rating}."""
    history = {}
    with open(DATA_DIR / "elo_history.csv", "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            year = int(row["year"])
            team = row["team"]
            rating = float(row["rating"])
            history[(year, team)] = rating
    return history


def load_matches():
    """Carga partidos de mundiales. Devuelve lista de dicts."""
    matches = []
    with open(DATA_DIR / "worldcup_matches.csv", "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            year = int(row["tournament_id"].split("-")[1])
            if year not in MUNDIALES:
                continue
            matches.append({
                "year": year,
                "stage": row["stage_name"],
                "home": row["home_team_name"],
                "away": row["away_team_name"],
                "home_goals": int(row["home_team_score"]),
                "away_goals": int(row["away_team_score"]),
                "extra_time": int(row["extra_time"]),
                "penalties": int(row["penalty_shootout"]),
            })
    return matches


def get_elo_for_team(elo_history, year, team_en):
    """Busca rating Elo de un equipo en un año. Si no, usa año anterior."""
    # Primero intentar año exacto
    if (year, team_en) in elo_history:
        return elo_history[(year, team_en)]
    # Intentar año anterior
    if (year - 1, team_en) in elo_history:
        return elo_history[(year - 1, team_en)]
    # Intentar 2 años antes
    if (year - 2, team_en) in elo_history:
        return elo_history[(year - 2, team_en)]
    return None


def brier_score(probs, outcome_idx):
    """Brier score para un outcome dado.
    probs: [p_home, p_draw, p_away]
    outcome_idx: 0=home, 1=draw, 2=away
    """
    target = [0.0, 0.0, 0.0]
    target[outcome_idx] = 1.0
    return sum((p - t) ** 2 for p, t in zip(probs, target))


def brier_binary(prob, occurred):
    """Brier score para evento binario."""
    return (prob - (1.0 if occurred else 0.0)) ** 2


def main():
    print("=" * 60)
    print("TACTIQO BACKTESTING")
    print("=" * 60)
    print()

    teams = load_teams()
    elo_history = load_elo_history()
    matches = load_matches()

    print(f"Equipos en teams.json: {len(teams)}")
    print(f"Partidos a evaluar: {len(matches)} (mundiales {MUNDIALES})")
    print()

    # Contadores por métrica
    brier_1x2 = []
    brier_over = []
    brier_btts = []
    brier_home = []
    brier_draw = []
    brier_away = []

    skipped = []
    evaluated = 0

    for m in matches:
        year = m["year"]
        home_en = m["home"]
        away_en = m["away"]

        # Buscar en teams.json (necesitamos nombre en español)
        home_es = EN_TO_ES.get(home_en)
        away_es = EN_TO_ES.get(away_en)

        if not home_es or not away_es:
            skipped.append(f"{year}: {home_en} vs {away_en} (sin mapeo)")
            continue

        if home_es not in teams or away_es not in teams:
            skipped.append(f"{year}: {home_en} vs {away_en} (no en teams.json)")
            continue

        # Obtener attack/defense de teams.json
        home_data = teams[home_es]
        away_data = teams[away_es]

        # Obtener Elo histórico
        home_elo = get_elo_for_team(elo_history, year, home_en)
        away_elo = get_elo_for_team(elo_history, year, away_en)

        if home_elo is None or away_elo is None:
            skipped.append(f"{year}: {home_en} ({home_elo}) vs {away_en} ({away_elo}) (sin Elo)")
            continue

        # Crear TeamStrength con Elo histórico
        home_ts = TeamStrength(
            id=home_data["id"],
            name=home_es,
            elo=home_elo,
            attack=home_data["attack"],
            defense=home_data["defense"],
        )
        away_ts = TeamStrength(
            id=away_data["id"],
            name=away_es,
            elo=away_elo,
            attack=away_data["attack"],
            defense=away_data["defense"],
        )

        # Predecir
        pred = predict_match(home_ts, away_ts, neutral=True)

        # Resultado real
        hg = m["home_goals"]
        ag = m["away_goals"]

        if hg > ag:
            outcome = 0  # home
        elif hg == ag:
            outcome = 1  # draw
        else:
            outcome = 2  # away

        probs = [pred.prob_home, pred.prob_draw, pred.prob_away]

        # Brier score 1X2
        brier_1x2.append(brier_score(probs, outcome))
        brier_home.append(brier_binary(pred.prob_home, outcome == 0))
        brier_draw.append(brier_binary(pred.prob_draw, outcome == 1))
        brier_away.append(brier_binary(pred.prob_away, outcome == 2))

        # Over 2.5
        over_occurred = (hg + ag) > 2
        brier_over.append(brier_binary(pred.over_2_5, over_occurred))

        # BTTS
        btts_occurred = hg > 0 and ag > 0
        brier_btts.append(brier_binary(pred.btts, btts_occurred))

        evaluated += 1

    # -- Reporte --
    print(f"Partidos evaluados: {evaluated}")
    print(f"Partidos saltados: {len(skipped)}")
    print()

    if evaluated == 0:
        print("ERROR: No se pudo evaluar ningún partido.")
        for s in skipped[:20]:
            print(f"  - {s}")
        return

    # Brier scores
    print("-" * 50)
    print("METRICAS DE CALIBRACION (Brier Score)")
    print("-" * 50)
    print(f"  1X2 (promedio):        {mean(brier_1x2):.4f}")
    print(f"  Victoria local:        {mean(brier_home):.4f}")
    print(f"  Empate:                {mean(brier_draw):.4f}")
    print(f"  Victoria visita:       {mean(brier_away):.4f}")
    print(f"  Over 2.5:              {mean(brier_over):.4f}")
    print(f"  BTTS:                  {mean(brier_btts):.4f}")
    print()

    # Baselines
    print("-" * 50)
    print("BASELINES (para comparar)")
    print("-" * 50)
    print("  Random 1X2 (1/3 cada): ~0.6667  (3-outcome)")
    print("  Random binario (0.5):  ~0.2500")
    print()

    # Calibracion por outcome
    home_probs = [p[0] for p in zip([pred.prob_home for pred in []])]
    # No tengo acceso a las preds individuales acá, dejémoslo simple

    print("-" * 50)
    print("DESGLOSE POR MUNDIAL")
    print("-" * 50)

    # Re-calcular por mundial
    for year in MUNDIALES:
        y_brier = []
        y_over = []
        y_btts = []
        y_count = 0

        for m in matches:
            if m["year"] != year:
                continue
            home_en = m["home"]
            away_en = m["away"]
            home_es = EN_TO_ES.get(home_en)
            away_es = EN_TO_ES.get(away_en)
            if not home_es or not away_es:
                continue
            if home_es not in teams or away_es not in teams:
                continue
            home_elo = get_elo_for_team(elo_history, year, home_en)
            away_elo = get_elo_for_team(elo_history, year, away_en)
            if home_elo is None or away_elo is None:
                continue

            home_ts = TeamStrength(
                id=teams[home_es]["id"], name=home_es,
                elo=home_elo, attack=teams[home_es]["attack"], defense=teams[home_es]["defense"]
            )
            away_ts = TeamStrength(
                id=teams[away_es]["id"], name=away_es,
                elo=away_elo, attack=teams[away_es]["attack"], defense=teams[away_es]["defense"]
            )
            pred = predict_match(home_ts, away_ts, neutral=True)

            hg, ag = m["home_goals"], m["away_goals"]
            if hg > ag:
                outcome = 0
            elif hg == ag:
                outcome = 1
            else:
                outcome = 2

            probs = [pred.prob_home, pred.prob_draw, pred.prob_away]
            y_brier.append(brier_score(probs, outcome))
            y_over.append(brier_binary(pred.over_2_5, (hg + ag) > 2))
            y_btts.append(brier_binary(pred.btts, hg > 0 and ag > 0))
            y_count += 1

        if y_count > 0:
            print(f"  {year}: {y_count} partidos | 1X2={mean(y_brier):.4f} | Over={mean(y_over):.4f} | BTTS={mean(y_btts):.4f}")

    print()
    print("=" * 60)

    # Mostrar algunos skipped si hay
    if skipped:
        print("\nPrimeros 10 partidos saltados:")
        for s in skipped[:10]:
            print(f"  - {s}")


if __name__ == "__main__":
    main()
