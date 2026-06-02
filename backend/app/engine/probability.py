"""Motor probabilistico de partidos.

Combina dos enfoques complementarios:

1. Elo -> probabilidad de resultado (1X2) via diferencia de rating.
2. Modelo Poisson bivariado (independiente) -> distribucion de goles, de la
   que derivamos 1X2, marcadores exactos, over/under, ambos marcan, etc.

El lambda (goles esperados) de cada equipo se modela como:

    lambda_local = base_attack_local * (defense_visitante / def_liga) * ajuste_elo * ventaja_local
    lambda_visitante = base_attack_visitante * (defense_local / def_liga) * ajuste_elo

donde ajuste_elo escala los goles segun la diferencia de Elo, de forma que
equipos muy superiores marcan mas y reciben menos.
"""
from __future__ import annotations

from dataclasses import dataclass
from functools import lru_cache
from math import exp, factorial
from typing import Dict, List

# Constantes del modelo (calibrables)
ELO_DIVISOR = 400.0          # escala estandar de Elo
HOME_ADVANTAGE_ELO = 65.0    # bonus de Elo por jugar de local (0 en sede neutral)
LEAGUE_AVG_DEFENSE = 1.05    # defensa "promedio" de referencia
ELO_GOAL_SENSITIVITY = 0.0018  # cuanto desplaza la dif. de Elo a los goles esperados
MAX_GOALS = 10               # tope para la grilla de marcadores


@dataclass
class TeamStrength:
    id: str
    name: str
    elo: float
    attack: float
    defense: float


def elo_expected_score(elo_a: float, elo_b: float, home_advantage: float = 0.0) -> float:
    """Probabilidad esperada (incluye empates como medio punto) del equipo A."""
    diff = (elo_a + home_advantage) - elo_b
    return 1.0 / (1.0 + 10 ** (-diff / ELO_DIVISOR))


def _poisson_pmf(k: int, lam: float) -> float:
    return exp(-lam) * lam ** k / factorial(k)


def expected_goals(
    home: TeamStrength,
    away: TeamStrength,
    neutral: bool = True,
) -> tuple[float, float]:
    """Calcula los goles esperados (lambda) de cada equipo."""
    home_adv = 0.0 if neutral else HOME_ADVANTAGE_ELO
    elo_diff = (home.elo + home_adv) - away.elo

    # factor multiplicativo segun diferencia de Elo (exponencial suave)
    elo_factor_home = exp(ELO_GOAL_SENSITIVITY * elo_diff)
    elo_factor_away = exp(-ELO_GOAL_SENSITIVITY * elo_diff)

    lam_home = home.attack * (away.defense / LEAGUE_AVG_DEFENSE) * elo_factor_home
    lam_away = away.attack * (home.defense / LEAGUE_AVG_DEFENSE) * elo_factor_away

    # limites de cordura
    lam_home = max(0.15, min(lam_home, 5.0))
    lam_away = max(0.15, min(lam_away, 5.0))
    return lam_home, lam_away


def score_matrix(lam_home: float, lam_away: float, max_goals: int = MAX_GOALS) -> List[List[float]]:
    """Matriz de probabilidad de marcadores (independencia de Poisson)."""
    home_p = [_poisson_pmf(i, lam_home) for i in range(max_goals + 1)]
    away_p = [_poisson_pmf(j, lam_away) for j in range(max_goals + 1)]
    return [[home_p[i] * away_p[j] for j in range(max_goals + 1)] for i in range(max_goals + 1)]


@dataclass
class MatchPrediction:
    home_id: str
    away_id: str
    lambda_home: float
    lambda_away: float
    prob_home: float
    prob_draw: float
    prob_away: float
    expected_home_goals: float
    expected_away_goals: float
    top_scorelines: List[dict]
    over_2_5: float
    btts: float          # both teams to score
    elo_win_prob: float  # prob de victoria via Elo puro (sin empate)


def predict_match(home: TeamStrength, away: TeamStrength, neutral: bool = True) -> MatchPrediction:
    lam_home, lam_away = expected_goals(home, away, neutral=neutral)
    matrix = score_matrix(lam_home, lam_away)

    p_home = p_draw = p_away = over = btts = 0.0
    scorelines: List[dict] = []
    for i, row in enumerate(matrix):
        for j, p in enumerate(row):
            if i > j:
                p_home += p
            elif i == j:
                p_draw += p
            else:
                p_away += p
            if i + j > 2:
                over += p
            if i > 0 and j > 0:
                btts += p
            scorelines.append({"home": i, "away": j, "p": p})

    scorelines.sort(key=lambda s: s["p"], reverse=True)
    top = [
        {"score": f"{s['home']}-{s['away']}", "prob": round(s["p"], 4)}
        for s in scorelines[:6]
    ]

    elo_e = elo_expected_score(home.elo, away.elo, 0.0 if neutral else HOME_ADVANTAGE_ELO)

    total = p_home + p_draw + p_away
    return MatchPrediction(
        home_id=home.id,
        away_id=away.id,
        lambda_home=round(lam_home, 3),
        lambda_away=round(lam_away, 3),
        prob_home=round(p_home / total, 4),
        prob_draw=round(p_draw / total, 4),
        prob_away=round(p_away / total, 4),
        expected_home_goals=round(lam_home, 2),
        expected_away_goals=round(lam_away, 2),
        top_scorelines=top,
        over_2_5=round(over, 4),
        btts=round(btts, 4),
        elo_win_prob=round(elo_e, 4),
    )
