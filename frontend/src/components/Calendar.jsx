import { useEffect, useState } from "react";
import { api } from "../api.js";
import { Loader2, CalendarDays, MapPin, ChevronDown, ChevronUp } from "lucide-react";
import Flag from "./Flag.jsx";

const DAY_NAMES = ["Dom", "Lun", "Mar", "Mié", "Jue", "Vie", "Sáb"];

function fmtDate(iso) {
  const d = new Date(iso + "T00:00:00");
  return `${DAY_NAMES[d.getDay()]} ${String(d.getDate()).padStart(2, "0")}/${String(
    d.getMonth() + 1
  ).padStart(2, "0")}`;
}

export default function Calendar({ timezone }) {
  const [data, setData] = useState(null);
  const [error, setError] = useState(null);
  const [active, setActive] = useState("1");

  useEffect(() => {
    api.fixtures().then((d) => setData(d.matchdays)).catch((e) => setError(e.message));
  }, []);

  if (error)
    return (
      <div className="card p-4 border-red-500/30 text-red-300 text-sm">
        No se pudo cargar el calendario: {error}
      </div>
    );
  if (!data)
    return (
      <div className="flex items-center gap-2 text-slate-400">
        <Loader2 className="animate-spin" size={18} /> Cargando calendario...
      </div>
    );

  const days = Object.keys(data).sort();
  const matches = data[active] || [];

  // agrupar por fecha (día)
  const byDate = {};
  for (const m of matches) {
    (byDate[m.date] = byDate[m.date] || []).push(m);
  }

  return (
    <div>
      <div className="flex gap-2 mb-5">
        {days.map((d) => {
          const count = (data[d] || []).length;
          return (
            <button
              key={d}
              onClick={() => setActive(d)}
              className={`flex items-center gap-2 px-4 py-2 rounded-xl text-sm font-medium transition ${
                active === d ? "bg-accent text-ink" : "bg-white/5 text-slate-300 hover:bg-white/10"
              }`}
            >
              <CalendarDays size={15} /> Fecha {d}
              <span className="text-xs opacity-70">({count})</span>
            </button>
          );
        })}
      </div>

      {matches.length === 0 ? (
        <div className="card p-6 text-center text-slate-400 text-sm">
          La Fecha {active} todavía no está cargada.
        </div>
      ) : (
        <div className="space-y-6">
          {Object.entries(byDate).map(([date, ms]) => (
            <div key={date}>
              <h3 className="text-sm font-semibold text-accent mb-2">{fmtDate(date)}</h3>
              <div className="grid gap-2">
                {ms.map((m, i) => (
                  <MatchRow key={i} m={m} convertTime={timezone.convertTime} />
                ))}
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

function MatchRow({ m, convertTime }) {
  const [expanded, setExpanded] = useState(false);
  const displayTime = convertTime ? convertTime(m.time, m.utc_offset) : m.time;
  const p = m.prediction;
  const segs = p
    ? [
        { v: p.prob_home, color: "bg-accent" },
        { v: p.prob_draw, color: "bg-slate-500" },
        { v: p.prob_away, color: "bg-blue-400" },
      ]
    : [];

  return (
    <div className={`card flex flex-col transition ${expanded ? "ring-1 ring-accent/30" : "hover:bg-white/5 hover:ring-1 hover:ring-accent/20"}`}>
      {/* Fila principal — solo datos del partido */}
      <div
        onClick={() => setExpanded((v) => !v)}
        className="p-3 flex items-center gap-3 cursor-pointer"
      >
        {/* Izquierda: info básica */}
        <div className="flex items-center gap-2 shrink-0 w-[140px]">
          <span className="text-xs text-slate-500 tabular-nums">{displayTime}</span>
          <span className="text-[10px] px-1.5 py-0.5 rounded bg-white/10 text-slate-300">
            {m.group}
          </span>
          {m.venue && (
            <span className="text-[10px] text-slate-500 flex items-center gap-0.5 truncate">
              <MapPin size={10} />
              {m.venue.city}
            </span>
          )}
        </div>

        {/* Centro: equipos alineados en grid de 5 columnas */}
        <div className="flex-1 grid grid-cols-[1fr_24px_32px_24px_1fr] items-center gap-2 min-w-0">
          {/* Nombre local — derecha */}
          <span className="font-medium truncate text-right">{m.home.name}</span>
          {/* Bandera local */}
          <span className="flex justify-center">
            <Flag
              teamId={m.home.id}
              className="w-5 h-3.5 rounded-sm ring-1 ring-white/10"
            />
          </span>
          {/* VS — centrado */}
          <span className="text-slate-500 text-sm text-center">vs</span>
          {/* Bandera visita */}
          <span className="flex justify-center">
            <Flag
              teamId={m.away.id}
              className="w-5 h-3.5 rounded-sm ring-1 ring-white/10"
            />
          </span>
          {/* Nombre visita — izquierda */}
          <span className="font-medium truncate text-left">{m.away.name}</span>
        </div>

        {/* Derecha: chevron */}
        <span className="text-slate-500 shrink-0 w-6 text-right">
          {expanded ? <ChevronUp size={16} /> : <ChevronDown size={16} />}
        </span>
      </div>

      {/* Panel expandido inline */}
      {expanded && p && (
        <div className="px-3 pb-3 border-t border-white/5 pt-3">
          <div className="flex justify-between text-sm mb-2">
            <span className="text-slate-300 truncate max-w-[33%]">
              {m.home.name} <b>{(p.prob_home * 100).toFixed(1)}%</b>
            </span>
            <span className="text-slate-300 truncate max-w-[33%] text-center">
              Empate <b>{(p.prob_draw * 100).toFixed(1)}%</b>
            </span>
            <span className="text-slate-300 truncate max-w-[33%] text-right">
              {m.away.name} <b>{(p.prob_away * 100).toFixed(1)}%</b>
            </span>
          </div>
          <div className="flex h-2.5 rounded-full overflow-hidden mb-4">
            {segs.map((s, i) => (
              <div key={i} className={s.color} style={{ width: `${s.v * 100}%` }} />
            ))}
          </div>

          <div className="grid grid-cols-2 sm:grid-cols-4 gap-2 text-sm mb-4">
            <InlineStat label="Goles esperados (local)" value={p.expected_home_goals} />
            <InlineStat label="Goles esperados (visita)" value={p.expected_away_goals} />
            <InlineStat label="Over 2.5 goles" value={`${(p.over_2_5 * 100).toFixed(0)}%`} />
            <InlineStat label="Ambos marcan" value={`${(p.btts * 100).toFixed(0)}%`} />
          </div>

          <h4 className="text-xs font-semibold mb-2 text-slate-400 uppercase tracking-wide">
            Marcadores más probables
          </h4>
          <div className="grid grid-cols-3 sm:grid-cols-6 gap-2">
            {(p.top_scorelines || []).map((s) => (
              <div key={s.score} className="bg-white/5 rounded-lg px-2 py-1.5 text-center">
                <div className="font-bold tabular-nums text-sm">{s.score}</div>
                <div className="text-[11px] text-slate-400">{(s.prob * 100).toFixed(1)}%</div>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}

function InlineStat({ label, value }) {
  return (
    <div className="bg-white/5 rounded-lg px-3 py-2">
      <div className="text-[11px] text-slate-400">{label}</div>
      <div className="font-semibold tabular-nums">{value}</div>
    </div>
  );
}
