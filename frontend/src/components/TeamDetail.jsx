import { useEffect, useState } from "react";
import { api } from "../api.js";
import { confBadge } from "../utils.js";
import { ArrowLeft, Loader2, Shield, User } from "lucide-react";

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

function Detail({ data }) {
  const t = data.team;
  const players = data.players || [];
  const totalValue = players.reduce((s, p) => s + (p.market_value_eur || 0), 0);

  return (
    <div className="space-y-6">
      {/* Cabecera */}
      <div className="card p-5">
        <div className="flex flex-wrap items-center gap-3">
          <div className="p-2 rounded-xl bg-accent/15 text-accent">
            <Shield size={26} />
          </div>
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

        <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 mt-5">
          <Stat label="Ranking FIFA" value={t.fifa_rank ? `#${t.fifa_rank}` : "—"} />
          <Stat label="Elo" value={Math.round(t.elo)} />
          <Stat label="Convocados" value={players.length || "—"} />
          <Stat label="Valor plantel" value={totalValue ? fmtMoney(totalValue) : "—"} />
        </div>
      </div>

      {!data.has_squad ? (
        <div className="card p-6 text-center text-slate-400 text-sm">
          El plantel de esta selección todavía no está cargado.
        </div>
      ) : (
        POS_GROUPS.map((pg) => {
          const list = players.filter((p) => p.position === pg.key);
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
