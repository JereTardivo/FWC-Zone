"""Entrena un modelo Gradient Boosting sobre features de equipos como
alternativa al modelo Elo/Poisson puro.

Features:
    elo_diff, elo_sum, attack_diff, defense_diff, rank_diff,
    elo_home, elo_away, attack_home, defense_home, attack_away, defense_away,
    rank_home, rank_away, confederation_same

Target: 0=home win, 1=draw, 2=away win

Uso:
    cd backend
    python -m scripts.train_ml_model
"""

import csv
import json
import sys
from pathlib import Path

import joblib
import numpy as np
from sklearn.ensemble import GradientBoostingClassifier
from sklearn.model_selection import cross_val_score, StratifiedKFold
from sklearn.metrics import log_loss, brier_score_loss
from sklearn.preprocessing import StandardScaler

sys.path.insert(0, str(Path(__file__).parent.parent))
from app.engine.probability import predict_match, TeamStrength

DATA_DIR = Path(__file__).parent.parent / "app" / "data"
MODEL_PATH = DATA_DIR / "ml_model.joblib"
SCALER_PATH = DATA_DIR / "ml_scaler.joblib"

# Mapeo de nombres
NAME_MAP = {
    "Argentina": "Argentina", "France": "Francia", "Spain": "España",
    "England": "Inglaterra", "Brazil": "Brasil", "Portugal": "Portugal",
    "Netherlands": "Países Bajos", "Belgium": "Bélgica", "Germany": "Alemania",
    "Croatia": "Croacia", "Uruguay": "Uruguay", "Colombia": "Colombia",
    "Morocco": "Marruecos", "United States": "Estados Unidos",
    "Mexico": "México", "Switzerland": "Suiza", "Japan": "Japón",
    "Senegal": "Senegal", "Austria": "Austria", "South Korea": "Corea del Sur",
    "Ecuador": "Ecuador", "Canada": "Canadá", "Australia": "Australia",
    "Egypt": "Egipto", "Ivory Coast": "Costa de Marfil", "Iran": "Irán",
    "Tunisia": "Túnez", "Paraguay": "Paraguay", "Scotland": "Escocia",
    "Norway": "Noruega", "Qatar": "Catar", "Saudi Arabia": "Arabia Saudita",
    "Ghana": "Ghana", "Panama": "Panamá", "Algeria": "Argelia",
    "Uzbekistan": "Uzbekistán", "Jordan": "Jordania", "South Africa": "Sudáfrica",
    "Cape Verde": "Cabo Verde", "New Zealand": "Nueva Zelanda",
    "Czechia": "República Checa", "Sweden": "Suecia", "Turkey": "Turquía",
    "DR Congo": "RD Congo", "Congo": "Congo",
    "Bosnia and Herzegovina": "Bosnia y Herzegovina", "Iraq": "Irak",
    "Haiti": "Haití", "Curaçao": "Curazao",
}
EN_TO_ES = {v: k for k, v in NAME_MAP.items()}


def load_teams():
    with open(DATA_DIR / "teams.json", "r", encoding="utf-8") as f:
        data = json.load(f)
    by_name = {}
    for t in data["teams"]:
        by_name[t["name"]] = {
            "id": t["id"], "elo": t["elo"], "attack": t["attack"],
            "defense": t["defense"], "fifa_rank": t.get("fifa_rank", 50),
            "confederation": t.get("confederation", "UNKNOWN"),
        }
    return by_name


def load_elo_history():
    history = {}
    with open(DATA_DIR / "elo_history.csv", "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            year = int(row["year"])
            team = row["team"]
            rating = float(row["rating"])
            history[(year, team)] = rating
    return history


def get_elo(elo_history, year, team_en):
    for dy in [0, -1, -2]:
        if (year + dy, team_en) in elo_history:
            return elo_history[(year + dy, team_en)]
    return None


def estimate_from_elo(elo):
    """Estima attack/defense/rank a partir del Elo usando regresion lineal
    sobre los equipos conocidos de teams.json."""
    # Regresiones simples aproximadas:
    # attack ~ 0.002 * elo - 1.8  (ARG 2080 -> 2.06, FRA 2120 -> 2.1)
    # defense ~ -0.0015 * elo + 3.8 (ARG 2080 -> 0.88)
    # rank ~ max(1, int(2100 - elo) / 5)
    attack = max(0.5, 0.0018 * elo - 1.65)
    defense = max(0.5, -0.0012 * elo + 3.3)
    rank = max(1, int((2200 - elo) / 4.5))
    return attack, defense, rank


def load_all_matches():
    """Carga todos los mundiales desde 1998 (Elo mas confiable)."""
    matches = []
    with open(DATA_DIR / "worldcup_matches.csv", "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            year = int(row["tournament_id"].split("-")[1])
            if year < 1998:
                continue
            # Ignorar partidos con penales (resultado ya decidido)
            if int(row["penalty_shootout"]):
                continue
            hg = int(row["home_team_score"])
            ag = int(row["away_team_score"])
            # Target
            if hg > ag:
                outcome = 0
            elif hg == ag:
                outcome = 1
            else:
                outcome = 2
            matches.append({
                "year": year,
                "home_en": row["home_team_name"],
                "away_en": row["away_team_name"],
                "home_goals": hg,
                "away_goals": ag,
                "outcome": outcome,
                "stage": row["stage_name"],
            })
    return matches


def build_dataset(matches, teams, elo_history):
    """Construye matriz X, y."""
    X = []
    y = []
    skipped = 0

    for m in matches:
        year = m["year"]
        home_en = m["home_en"]
        away_en = m["away_en"]

        home_es = EN_TO_ES.get(home_en, home_en)
        away_es = EN_TO_ES.get(away_en, away_en)

        # Elo historico
        elo_h = get_elo(elo_history, year, home_en)
        elo_a = get_elo(elo_history, year, away_en)
        if elo_h is None or elo_a is None:
            skipped += 1
            continue

        # Features de teams.json (o estimadas)
        if home_es in teams:
            th = teams[home_es]
            att_h, def_h, rank_h = th["attack"], th["defense"], th["fifa_rank"]
            conf_h = th["confederation"]
        else:
            att_h, def_h, rank_h = estimate_from_elo(elo_h)
            conf_h = "UNKNOWN"

        if away_es in teams:
            ta = teams[away_es]
            att_a, def_a, rank_a = ta["attack"], ta["defense"], ta["fifa_rank"]
            conf_a = ta["confederation"]
        else:
            att_a, def_a, rank_a = estimate_from_elo(elo_a)
            conf_a = "UNKNOWN"

        features = [
            elo_h - elo_a,                # elo_diff
            elo_h + elo_a,                # elo_sum
            att_h - att_a,                # attack_diff
            def_h - def_a,                # defense_diff
            rank_h - rank_a,              # rank_diff
            elo_h,
            elo_a,
            att_h,
            def_h,
            att_a,
            def_a,
            rank_h,
            rank_a,
            1.0 if conf_h == conf_a else 0.0,  # same_confederation
            1.0 if m["stage"] != "group stage" else 0.0,  # knockout
        ]
        X.append(features)
        y.append(m["outcome"])

    return np.array(X), np.array(y), skipped


def brier_1x2(y_true, y_proba):
    """Brier score para 3 clases."""
    n = len(y_true)
    scores = []
    for yt, yp in zip(y_true, y_proba):
        target = np.zeros(3)
        target[yt] = 1.0
        scores.append(np.sum((yp - target) ** 2))
    return np.mean(scores)


def main():
    print("=" * 60)
    print("TACTIQO ML MODEL TRAINING")
    print("=" * 60)
    print()

    teams = load_teams()
    elo_history = load_elo_history()
    matches = load_all_matches()
    print(f"Partidos cargados (1998-2022, sin penales): {len(matches)}")

    X, y, skipped = build_dataset(matches, teams, elo_history)
    print(f"Partidos con features completos: {len(y)}")
    print(f"Partidos saltados (sin Elo): {skipped}")
    print()

    if len(y) == 0:
        print("ERROR: No hay datos suficientes.")
        return

    # Balance de clases
    print("Distribucion de resultados:")
    for label, name in [(0, "Home"), (1, "Draw"), (2, "Away")]:
        count = np.sum(y == label)
        print(f"  {name}: {count} ({count / len(y) * 100:.1f}%)")
    print()

    # Escalar features
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)

    # Entrenar
    print("Entrenando GradientBoostingClassifier...")
    clf = GradientBoostingClassifier(
        n_estimators=200,
        max_depth=4,
        learning_rate=0.1,
        subsample=0.8,
        random_state=42,
    )

    # Cross-validation
    cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)
    acc_scores = cross_val_score(clf, X_scaled, y, cv=cv, scoring="accuracy")
    logloss_scores = cross_val_score(clf, X_scaled, y, cv=cv, scoring="neg_log_loss")

    print(f"  CV Accuracy:  {acc_scores.mean():.4f} (+/- {acc_scores.std():.4f})")
    print(f"  CV LogLoss:   {-logloss_scores.mean():.4f} (+/- {logloss_scores.std():.4f})")
    print()

    # Entrenar en todo el dataset para guardar
    clf.fit(X_scaled, y)
    y_proba = clf.predict_proba(X_scaled)

    brier = brier_1x2(y, y_proba)
    print(f"  Train Brier (1X2): {brier:.4f}")
    print()

    # Feature importance
    feature_names = [
        "elo_diff", "elo_sum", "attack_diff", "defense_diff", "rank_diff",
        "elo_home", "elo_away", "attack_home", "defense_home", "attack_away",
        "defense_away", "rank_home", "rank_away", "same_conf", "knockout",
    ]
    print("Feature importances:")
    for name, imp in sorted(
        zip(feature_names, clf.feature_importances_), key=lambda x: -x[1]
    ):
        print(f"  {name:20s}: {imp:.4f}")
    print()

    # Guardar modelo
    joblib.dump(clf, MODEL_PATH)
    joblib.dump(scaler, SCALER_PATH)
    print(f"Modelo guardado en: {MODEL_PATH}")
    print(f"Scaler guardado en: {SCALER_PATH}")

    # Comparar con modelo Elo/Poisson
    print()
    print("=" * 60)
    print("COMPARACION vs MODELO ELO/POISSON")
    print("=" * 60)

    elo_briers = []
    for m in matches:
        if m["outcome"] is None:
            continue
        year = m["year"]
        home_en = m["home_en"]
        away_en = m["away_en"]
        home_es = EN_TO_ES.get(home_en, home_en)
        away_es = EN_TO_ES.get(away_en, away_en)
        elo_h = get_elo(elo_history, year, home_en)
        elo_a = get_elo(elo_history, year, away_en)
        if elo_h is None or elo_a is None:
            continue
        if home_es not in teams or away_es not in teams:
            continue

        th = teams[home_es]
        ta = teams[away_es]
        home_ts = TeamStrength(id=th["id"], name=home_es, elo=elo_h, attack=th["attack"], defense=th["defense"])
        away_ts = TeamStrength(id=ta["id"], name=away_es, elo=elo_a, attack=ta["attack"], defense=ta["defense"])
        pred = predict_match(home_ts, away_ts, neutral=True)

        probs = [pred.prob_home, pred.prob_draw, pred.prob_away]
        target = np.zeros(3)
        target[m["outcome"]] = 1.0
        elo_briers.append(np.sum((np.array(probs) - target) ** 2))

    if elo_briers:
        print(f"  ML   Brier (train): {brier:.4f}")
        print(f"  Elo  Brier:         {np.mean(elo_briers):.4f}")
    print()


if __name__ == "__main__":
    main()
