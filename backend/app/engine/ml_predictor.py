"""Predictor ML basado en Gradient Boosting como alternativa al Elo/Poisson.

Uso:
    from app.engine.ml_predictor import MLPredictor
    predictor = MLPredictor()
    probs = predictor.predict(home_team, away_team)
    # probs = {"home": 0.45, "draw": 0.30, "away": 0.25}
"""

import json
from pathlib import Path

import joblib
import numpy as np

DATA_DIR = Path(__file__).parent.parent / "data"


def _estimate_from_elo(elo: float):
    """Estima attack/defense/rank a partir de Elo."""
    attack = max(0.5, 0.0018 * elo - 1.65)
    defense = max(0.5, -0.0012 * elo + 3.3)
    rank = max(1, int((2200 - elo) / 4.5))
    return attack, defense, rank


class MLPredictor:
    def __init__(self):
        self.model = None
        self.scaler = None
        self.teams = {}
        self._load()

    def _load(self):
        model_path = DATA_DIR / "ml_model.joblib"
        scaler_path = DATA_DIR / "ml_scaler.joblib"
        if model_path.exists():
            self.model = joblib.load(model_path)
        if scaler_path.exists():
            self.scaler = joblib.load(scaler_path)

        with open(DATA_DIR / "teams.json", "r", encoding="utf-8") as f:
            data = json.load(f)
        for t in data["teams"]:
            self.teams[t["name"]] = {
                "id": t["id"],
                "elo": t["elo"],
                "attack": t["attack"],
                "defense": t["defense"],
                "fifa_rank": t.get("fifa_rank", 50),
                "confederation": t.get("confederation", "UNKNOWN"),
            }

    def is_ready(self) -> bool:
        return self.model is not None and self.scaler is not None

    def predict(self, home_id: str, away_id: str, neutral: bool = True) -> dict:
        """Devuelve probabilidades 1X2 como dict.

        Si el modelo no esta cargado, devuelve None.
        """
        if not self.is_ready():
            return None

        # Buscar equipos por ID
        home = None
        away = None
        for name, info in self.teams.items():
            if info["id"] == home_id:
                home = info
                home_name = name
            if info["id"] == away_id:
                away = info
                away_name = name

        if home is None or away is None:
            return None

        features = self._build_features(home, away, home_name, away_name, neutral)
        X = self.scaler.transform([features])
        proba = self.model.predict_proba(X)[0]

        return {
            "prob_home": round(float(proba[0]), 4),
            "prob_draw": round(float(proba[1]), 4),
            "prob_away": round(float(proba[2]), 4),
            "model": "gradient_boosting",
        }

    def _build_features(self, home, away, home_name, away_name, neutral):
        elo_h = home["elo"]
        elo_a = away["elo"]
        att_h = home["attack"]
        def_h = home["defense"]
        rank_h = home["fifa_rank"]
        conf_h = home["confederation"]

        att_a = away["attack"]
        def_a = away["defense"]
        rank_a = away["fifa_rank"]
        conf_a = away["confederation"]

        return [
            elo_h - elo_a,
            elo_h + elo_a,
            att_h - att_a,
            def_h - def_a,
            rank_h - rank_a,
            elo_h,
            elo_a,
            att_h,
            def_h,
            att_a,
            def_a,
            rank_h,
            rank_a,
            1.0 if conf_h == conf_a else 0.0,
            0.0 if neutral else 1.0,  # knockout simplificado
        ]
