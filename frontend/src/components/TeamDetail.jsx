import { useEffect, useMemo, useState } from "react";
import { api } from "../api.js";
import { confBadge } from "../utils.js";
import Flag from "./Flag.jsx";
import {
  ArrowLeft,
  Loader2,
  User,
  Search,
  Star,
  Coins,
  LayoutGrid,
  List,
} from "lucide-react";

const POS_GROUPS = [
  { key: "GK", label: "Arqueros" },
  { key: "DF", label: "Defensores" },
  { key: "MF", label: "Mediocampistas" },
  { key: "FW", label: "Delanteros" },
];

const POS_COLOR = {
  GK: "bg-amber-500/15 text-amber-300",
  DF: "bg-sky-500/15 text-sky-300",
  MF: "bg-emerald-500/15 text-emerald-300",
  FW: "bg-rose-500/15 text-rose-300",
};

function fmtMoney(v) {
  if (v == null) return "—";
  if (v >= 1_000_000) return `€${(v / 1_000_000).toFixed(1)}M`;
  if (v >= 1_000) return `€${(v / 1_000).toFixed(0)}K`;
  return `€${v}`;
}

export default function TeamDetail({ teamId, onBack }) {
  const [data, setData] = useState(null);
  const [error, setError] = useState(null);

  useEffect(() => {
    setData(null);
    setError(null);
    api.team(teamId).then(setData).catch((e) => setError(e.message));
  }, [teamId]);

  return (
    <div>
      <button
        onClick={onBack}
        className="flex items-center gap-2 text-sm text-slate-300 hover:text-accent mb-5"
      >
        <ArrowLeft size={16} /> Volver
      </button>

      {error && (
        <div className="card p-4 border-red-500/30 text-red-300 text-sm">
          No se pudo cargar la selección: {error}
        </div>
      )}

      {!data && !error && (
        <div className="flex items-center gap-2 text-slate-400">
          <Loader2 className="animate-spin" size={18} /> Cargando selección...
        </div>
      )}

      {data && <Detail data={data} />}
    </div>
  );
}

const SORTS = [
  { key: "rating", label: "Rating" },
  { key: "value", label: "Valor" },
  { key: "name", label: "Nombre" },
];

function sortPlayers(list, sort) {
  const arr = [...list];
  if (sort === "name") {
    arr.sort((a, b) => a.name.localeCompare(b.name));
  } else if (sort === "value") {
    arr.sort((a, b) => (b.market_value_eur || 0) - (a.market_value_eur || 0));
  } else {
    arr.sort((a, b) => (b.fifa_rating || 0) - (a.fifa_rating || 0));
  }
  return arr;
}

function Detail({ data }) {
  const t = data.team;
  const players = data.players || [];
  const [view, setView] = useState("position");
  const [sort, setSort] = useState("rating");
  const [query, setQuery] = useState("");

  const stats = useMemo(() => {
    const rated = players.filter((p) => p.fifa_rating != null);
    const totalValue = players.reduce((s, p) => s + (p.market_value_eur || 0), 0);
    const avgRating = rated.length
      ? Math.round(rated.reduce((s, p) => s + p.fifa_rating, 0) / rated.length)
      : null;
    const topValue = players.reduce(
      (best, p) =>
        (p.market_value_eur || 0) > (best?.market_value_eur || 0) ? p : best,
      null
    );
    const topRated = rated.reduce(
      (best, p) => ((p.fifa_rating || 0) > (best?.fifa_rating || 0) ? p : best),
      null
    );
    return { totalValue, avgRating, topValue, topRated };
  }, [players]);

  const filtered = useMemo(() => {
    const q = query.trim().toLowerCase();
    if (!q) return players;
    return players.filter(
      (p) =>
        p.name.toLowerCase().includes(q) ||
        (p.club || "").toLowerCase().includes(q)
    );
  }, [players, query]);

  return (
    <div className="space-y-6">
      {/* Cabecera */}
      <div className="card p-5">
        <div className="flex flex-wrap items-center gap-3">
          <Flag
            teamId={t.id}
            className="w-12 h-8 rounded-md ring-1 ring-white/15 shrink-0"
          />
          <div className="flex-1">
            <h2 className="text-2xl font-extrabold">{t.name}</h2>
            <div className="flex items-center gap-2 mt-1 text-sm">
              <span className={`px-2 py-0.5 rounded ${confBadge(t.confederation)}`}>
                {t.confederation}
              </span>
              {data.group && (
                <span className="px-2 py-0.5 rounded bg-white/10 text-slate-300">
                  Grupo {data.group}
                </span>
              )}
              {data.coach && <span className="text-slate-400">DT: {data.coach}</span>}
            </div>
          </div>
        </div>

        <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-6 gap-3 mt-5">
          <Stat label="Ranking FIFA" value={t.fifa_rank ? `#${t.fifa_rank}` : "—"} />
          <Stat label="Elo" value={Math.round(t.elo)} />
          <Stat label="Convocados" value={players.length || "—"} />
          <Stat
            label="Rating medio"
            value={stats.avgRating != null ? stats.avgRating : "—"}
          />
          <Stat
            label="Valor plantel"
            value={stats.totalValue ? fmtMoney(stats.totalValue) : "—"}
          />
          <Stat
            label="Figura"
            value={
              stats.topValue ? (
                <span className="flex items-center gap-1 text-accent">
                  <Star size={12} className="fill-accent" />
                  {stats.topValue.name.split(" ").slice(-1)[0]}
                </span>
              ) : (
                "—"
              )
            }
          />
        </div>
      </div>

      {!data.has_squad ? (
        <div className="card p-6 text-center text-slate-400 text-sm">
          El plantel de esta selección todavía no está cargado.
        </div>
      ) : (
        <>
          {/* Controles */}
          <div className="card p-3 flex flex-wrap items-center gap-3">
            <div className="relative flex-1 min-w-[180px]">
              <Search
                size={15}
                className="absolute left-3 top-1/2 -translate-y-1/2 text-slate-500"
              />
              <input
                value={query}
                onChange={(e) => setQuery(e.target.value)}
                placeholder="Buscar jugador o club…"
                className="w-full bg-white/5 rounded-lg pl-9 pr-3 py-2 text-sm outline-none focus:ring-1 focus:ring-accent/50 placeholder:text-slate-500"
              />
            </div>

            <div className="flex items-center gap-1 bg-white/5 rounded-lg p-1">
              {SORTS.map((s) => (
                <button
                  key={s.key}
                  onClick={() => setSort(s.key)}
                  className={`px-2.5 py-1 rounded-md text-xs font-medium transition ${
                    sort === s.key
                      ? "bg-accent text-ink"
                      : "text-slate-300 hover:bg-white/10"
                  }`}
                >
                  {s.label}
                </button>
              ))}
            </div>

            <div className="flex items-center gap-1 bg-white/5 rounded-lg p-1">
              <button
                onClick={() => setView("position")}
                title="Por posición"
                className={`p-1.5 rounded-md transition ${
                  view === "position"
                    ? "bg-accent text-ink"
                    : "text-slate-300 hover:bg-white/10"
                }`}
              >
                <LayoutGrid size={15} />
              </button>
              <button
                onClick={() => setView("list")}
                title="Lista ordenada"
                className={`p-1.5 rounded-md transition ${
                  view === "list"
                    ? "bg-accent text-ink"
                    : "text-slate-300 hover:bg-white/10"
                }`}
              >
                <List size={15} />
              </button>
            </div>
          </div>

          {filtered.length === 0 ? (
            <div className="card p-6 text-center text-slate-400 text-sm">
              Sin resultados para “{query}”.
            </div>
          ) : view === "list" ? (
            <div className="card divide-y divide-white/5">
              {sortPlayers(filtered, sort).map((p, i) => (
                <PlayerRow key={p.name} p={p} rank={i + 1} />
              ))}
            </div>
          ) : (
            POS_GROUPS.map((pg) => {
              const list = sortPlayers(
                filtered.filter((p) => p.position === pg.key),
                sort
              );
              if (!list.length) return null;
              return (
                <div key={pg.key}>
                  <h3 className="font-semibold mb-3 flex items-center gap-2">
                    <span className={`text-xs px-2 py-0.5 rounded ${POS_COLOR[pg.key]}`}>
                      {pg.key}
                    </span>
                    {pg.label}
                    <span className="text-xs text-slate-500">({list.length})</span>
                  </h3>
                  <div className="grid sm:grid-cols-2 lg:grid-cols-3 gap-2">
                    {list.map((p) => (
                      <PlayerCard key={p.name} p={p} />
                    ))}
                  </div>
                </div>
              );
            })
          )}
        </>
      )}
    </div>
  );
}

function PlayerRow({ p, rank }) {
  return (
    <div className="flex items-center gap-3 px-3 py-2.5 hover:bg-white/5 transition">
      <span className="w-5 text-center text-xs tabular-nums text-slate-500">
        {rank}
      </span>
      <span
        className={`text-[10px] font-semibold px-1.5 py-0.5 rounded ${POS_COLOR[p.position]}`}
      >
        {p.position}
      </span>
      <div className="flex-1 min-w-0">
        <div className="font-medium truncate">{p.name}</div>
        <div className="text-xs text-slate-500 truncate">
          {p.club}
          {p.club_country ? ` · ${p.club_country}` : ""}
        </div>
      </div>
      <span className="flex items-center gap-1 text-xs tabular-nums text-slate-400 w-20 justify-end">
        <Coins size={12} className="text-slate-500" />
        {p.market_value_eur != null ? fmtMoney(p.market_value_eur) : "—"}
      </span>
      <span className="text-xs font-bold px-1.5 py-0.5 rounded bg-accent/20 text-accent w-9 text-center">
        {p.fifa_rating != null ? p.fifa_rating : "—"}
      </span>
    </div>
  );
}

function PlayerCard({ p }) {
  return (
    <div className="card p-3">
      <div className="flex items-center gap-2">
        <User size={15} className="text-slate-500" />
        <span className="font-medium flex-1">{p.name}</span>
        {p.fifa_rating != null && (
          <span className="text-xs font-bold px-1.5 py-0.5 rounded bg-accent/20 text-accent">
            {p.fifa_rating}
          </span>
        )}
      </div>
      <div className="text-xs text-slate-400 mt-1.5 flex items-center justify-between">
        <span>
          {p.club}
          {p.club_country ? ` · ${p.club_country}` : ""}
        </span>
        <span className="tabular-nums text-slate-500">
          {p.market_value_eur != null ? fmtMoney(p.market_value_eur) : ""}
        </span>
      </div>
      {(p.caps != null || p.goals != null) && (
        <div className="text-[11px] text-slate-500 mt-1 flex gap-3">
          {p.caps != null && <span>{p.caps} PJ</span>}
          {p.goals != null && <span>{p.goals} goles</span>}
        </div>
      )}
    </div>
  );
}

function Stat({ label, value }) {
  return (
    <div className="bg-white/5 rounded-lg px-3 py-2">
      <div className="text-xs text-slate-400">{label}</div>
      <div className="font-semibold tabular-nums">{value}</div>
    </div>
  );
}
