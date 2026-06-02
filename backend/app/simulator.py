"""Simulador Monte Carlo del Mundial 2026 completo.

Formato:
- 12 grupos de 4 (round robin, 3 partidos por equipo).
- Avanzan los 2 primeros de cada grupo (24) + los 8 mejores terceros = 32.
- Fase eliminatoria: R32 -> R16 -> QF -> SF -> FINAL + partido por el 3er puesto
  (perdedores de semis). Un solo partido por llave, desempate por penales modelado
  con prob. ~ Elo.

Cada simulacion (iteracion) juega el torneo entero muestreando goles con Poisson.
Repetimos N veces y agregamos frecuencias -> probabilidades.
"""
from __future__ import annotations

import random
from collections import defaultdict
from dataclasses import dataclass
from typing import Dict, List, Tuple

from .engine.probability import (
    TeamStrength,
    elo_expected_score,
    expected_goals,
)


@dataclass
class GroupResult:
    team_id: str
    points: int = 0
    gf: int = 0
    ga: int = 0
    played: int = 0

    @property
    def gd(self) -> int:
        return self.gf - self.ga


def _poisson(lam: float, rng: random.Random) -> int:
    """Generador de Poisson por el metodo de Knuth (sin numpy)."""
    import math

    L = math.exp(-lam)
    k = 0
    p = 1.0
    while True:
        k += 1
        p *= rng.random()
        if p <= L:
            return k - 1


def _play(home: TeamStrength, away: TeamStrength, rng: random.Random) -> Tuple[int, int]:
    lam_h, lam_a = expected_goals(home, away, neutral=True)
    return _poisson(lam_h, rng), _poisson(lam_a, rng)


def _knockout_winner(a: TeamStrength, b: TeamStrength, rng: random.Random) -> TeamStrength:
    gh, ga = _play(a, b, rng)
    if gh > ga:
        return a
    if ga > gh:
        return b
    # empate -> penales: probabilidad via Elo (suavizada hacia 50%)
    p_a = elo_expected_score(a.elo, b.elo)
    p_a = 0.5 + (p_a - 0.5) * 0.5  # penales son mas aleatorios
    return a if rng.random() < p_a else b


# ----------------- Bracket OFICIAL Mundial 2026 -----------------
# Cada R32 que recibe un 3ro acepta uno de un conjunto de grupos (tabla FIFA).
THIRD_SLOTS = [
    ("S1", set("ABCDF")),
    ("S2", set("CDFGH")),
    ("S7", set("BEFIJ")),
    ("S8", set("AEHIJ")),
    ("S11", set("CEFHI")),
    ("S12", set("EHIJK")),
    ("S15", set("EFGIJ")),
    ("S16", set("DEIJL")),
]

# 16 partidos de R32 (16avos), en orden P1..P16 (matches 73..88).
# Token: "1X"/"2X" = 1ro/2do del grupo X; "S#" = tercero asignado a ese slot.
R32_DEF = [
    ("1E", "S1"),    # P1  m73
    ("1I", "S2"),    # P2  m74
    ("2A", "2B"),    # P3  m75
    ("1F", "2C"),    # P4  m76
    ("2K", "2L"),    # P5  m77
    ("1H", "2J"),    # P6  m78
    ("1D", "S7"),    # P7  m79
    ("1G", "S8"),    # P8  m80
    ("1C", "2F"),    # P9  m81
    ("2E", "2I"),    # P10 m82
    ("1A", "S11"),   # P11 m83
    ("1L", "S12"),   # P12 m84
    ("1J", "2H"),    # P13 m85
    ("2D", "2G"),    # P14 m86
    ("1B", "S15"),   # P15 m87
    ("1K", "S16"),   # P16 m88
]

# R16 (octavos m89-96): pares de indices en la lista de ganadores de R32.
R16_PAIRS = [(0, 2), (1, 4), (3, 5), (6, 7), (8, 9), (10, 11), (12, 14), (13, 15)]
# QF (m97-100): pares de indices en ganadores de R16.
QF_PAIRS = [(0, 1), (4, 5), (2, 3), (6, 7)]
# SF (m101-102): pares de indices en ganadores de QF.
SF_PAIRS = [(0, 1), (2, 3)]


def assign_thirds(thirds_by_group: Dict[str, str], rng: random.Random) -> Dict[str, str]:
    """Asigna los 8 terceros clasificados a los slots respetando grupos permitidos.
    thirds_by_group: letra_grupo -> team_id. Devuelve slot_key -> team_id."""
    slots = list(THIRD_SLOTS)
    rng.shuffle(slots)
    available = dict(thirds_by_group)
    assignment: Dict[str, str] = {}

    def backtrack(i: int) -> bool:
        if i == len(slots):
            return True
        key, allowed = slots[i]
        candidates = [g for g in available if g in allowed]
        rng.shuffle(candidates)
        for g in candidates:
            tid = available.pop(g)
            assignment[key] = tid
            if backtrack(i + 1):
                return True
            del assignment[key]
            available[g] = tid
        return False

    if not backtrack(0):
        # fallback defensivo (no deberia ocurrir con la tabla FIFA)
        keys = [k for k, _ in slots]
        for key, tid in zip(keys, thirds_by_group.values()):
            assignment[key] = tid
    return assignment


class TournamentSimulator:
    def __init__(self, strengths: Dict[str, TeamStrength], groups: Dict[str, List[str]]):
        self.strengths = strengths
        self.groups = groups

    def _simulate_group(self, team_ids: List[str], rng: random.Random) -> List[GroupResult]:
        table = {tid: GroupResult(tid) for tid in team_ids}
        for i in range(len(team_ids)):
            for j in range(i + 1, len(team_ids)):
                a, b = team_ids[i], team_ids[j]
                gh, ga = _play(self.strengths[a], self.strengths[b], rng)
                ra, rb = table[a], table[b]
                ra.gf += gh; ra.ga += ga; rb.gf += ga; rb.ga += gh
                ra.played += 1; rb.played += 1
                if gh > ga:
                    ra.points += 3
                elif ga > gh:
                    rb.points += 3
                else:
                    ra.points += 1; rb.points += 1
        ranked = sorted(
            table.values(),
            key=lambda r: (r.points, r.gd, r.gf, rng.random()),
            reverse=True,
        )
        return ranked

    def simulate_once(self, rng: random.Random) -> dict:
        group_rank: Dict[str, List[GroupResult]] = {}
        for gid, team_ids in self.groups.items():
            group_rank[gid] = self._simulate_group(team_ids, rng)

        firsts = {gid: r[0].team_id for gid, r in group_rank.items()}
        seconds = {gid: r[1].team_id for gid, r in group_rank.items()}
        thirds = [(gid, r[2]) for gid, r in group_rank.items()]

        # 8 mejores terceros (por puntos, dif. de gol, goles a favor)
        best = sorted(
            thirds, key=lambda t: (t[1].points, t[1].gd, t[1].gf, rng.random()), reverse=True
        )[:8]
        thirds_by_group = {gid: gr.team_id for gid, gr in best}

        qualified = (
            list(firsts.values()) + list(seconds.values()) + list(thirds_by_group.values())
        )

        # resolver participantes de cada slot del bracket
        slot_team = assign_thirds(thirds_by_group, rng)
        pos: Dict[str, str] = {}
        for gid in self.groups:
            pos[f"1{gid}"] = firsts[gid]
            pos[f"2{gid}"] = seconds[gid]

        def resolve(token: str) -> str:
            return slot_team[token] if token.startswith("S") else pos[token]

        round_reached: Dict[str, str] = {tid: "R32" for tid in qualified}

        # R32 -> ganadores en orden P1..P16
        r32_winners: List[str] = []
        for a_tok, b_tok in R32_DEF:
            a, b = resolve(a_tok), resolve(b_tok)
            w = _knockout_winner(self.strengths[a], self.strengths[b], rng).id
            r32_winners.append(w)
            round_reached[w] = "R16"

        r16_winners = self._play_pairs(r32_winners, R16_PAIRS, rng)
        for w in r16_winners:
            round_reached[w] = "QF"
        qf_winners = self._play_pairs(r16_winners, QF_PAIRS, rng)
        for w in qf_winners:
            round_reached[w] = "SF"

        # Semifinales (m101, m102): guardamos ganador y perdedor de cada una
        sf_results: List[Tuple[str, str]] = []
        for i, j in SF_PAIRS:
            a, b = qf_winners[i], qf_winners[j]
            w = _knockout_winner(self.strengths[a], self.strengths[b], rng).id
            loser = b if w == a else a
            sf_results.append((w, loser))
            round_reached[w] = "FINAL"

        finalists = [sf_results[0][0], sf_results[1][0]]
        sf_losers = [sf_results[0][1], sf_results[1][1]]

        # Final (m104)
        champion = _knockout_winner(
            self.strengths[finalists[0]], self.strengths[finalists[1]], rng
        ).id
        runner_up = finalists[1] if champion == finalists[0] else finalists[0]

        # Partido por el 3er puesto (m103): perdedores de las semis
        third = _knockout_winner(
            self.strengths[sf_losers[0]], self.strengths[sf_losers[1]], rng
        ).id
        fourth = sf_losers[1] if third == sf_losers[0] else sf_losers[0]

        return {
            "champion": champion,
            "runner_up": runner_up,
            "third": third,
            "fourth": fourth,
            "finalists": finalists,
            "round_reached": round_reached,
            "group_firsts": list(firsts.values()),
            "qualified": qualified,
        }

    def _play_pairs(
        self, winners: List[str], pairs: List[Tuple[int, int]], rng: random.Random
    ) -> List[str]:
        return [
            _knockout_winner(self.strengths[winners[i]], self.strengths[winners[j]], rng).id
            for i, j in pairs
        ]

    def run(self, iterations: int = 10000, seed: int | None = None) -> dict:
        rng = random.Random(seed)
        all_ids = [tid for g in self.groups.values() for tid in g]
        champion_counts: Dict[str, int] = defaultdict(int)
        runner_up_counts: Dict[str, int] = defaultdict(int)
        third_counts: Dict[str, int] = defaultdict(int)
        final_counts: Dict[str, int] = defaultdict(int)
        qualify_counts: Dict[str, int] = defaultdict(int)
        win_group_counts: Dict[str, int] = defaultdict(int)

        for _ in range(iterations):
            res = self.simulate_once(rng)
            champion_counts[res["champion"]] += 1
            runner_up_counts[res["runner_up"]] += 1
            third_counts[res["third"]] += 1
            for tid in res["finalists"]:
                final_counts[tid] += 1
            for tid in res["qualified"]:
                qualify_counts[tid] += 1
            for tid in res["group_firsts"]:
                win_group_counts[tid] += 1

        results = []
        for tid in all_ids:
            podium = champion_counts[tid] + runner_up_counts[tid] + third_counts[tid]
            results.append({
                "team_id": tid,
                "champion_pct": round(100 * champion_counts[tid] / iterations, 2),
                "runner_up_pct": round(100 * runner_up_counts[tid] / iterations, 2),
                "third_pct": round(100 * third_counts[tid] / iterations, 2),
                "final_pct": round(100 * final_counts[tid] / iterations, 2),
                "podium_pct": round(100 * podium / iterations, 2),
                "qualify_pct": round(100 * qualify_counts[tid] / iterations, 2),
                "win_group_pct": round(100 * win_group_counts[tid] / iterations, 2),
            })
        results.sort(key=lambda r: r["champion_pct"], reverse=True)
        return {
            "iterations": iterations,
            "teams": results,
        }
