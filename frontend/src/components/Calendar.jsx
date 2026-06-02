import { useEffect, useState } from "react";
import { api } from "../api.js";
import { Loader2, CalendarDays } from "lucide-react";

const DAY_NAMES = ["Dom", "Lun", "Mar", "Mié", "Jue", "Vie", "Sáb"];

function fmtDate(iso) {
  const d = new Date(iso + "T00:00:00");
  return `${DAY_NAMES[d.getDay()]} ${String(d.getDate()).padStart(2, "0")}/${String(
    d.getMonth() + 1
  ).padStart(2, "0")}`;
}

export default function Calendar() {
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
                  <MatchRow key={i} m={m} />
                ))}
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

function MatchRow({ m }) {
  const p = m.prediction;
  const segs = p
    ? [
        { v: p.prob_home, color: "bg-accent" },
        { v: p.prob_draw, color: "bg-slate-500" },
        { v: p.prob_away, color: "bg-blue-400" },
      ]
    : [];

  return (
    <div className="card p-3 flex flex-col gap-2">
      <div className="flex items-center gap-3">
        <span className="text-xs text-slate-500 w-12 tabular-nums">{m.time}</span>
        <span className="text-[10px] px-1.5 py-0.5 rounded bg-white/10 text-slate-300">
          Grupo {m.group}
        </span>
        <span className="flex-1 text-right font-medium">{m.home.name}</span>
        <span className="text-slate-500 text-sm px-2">vs</span>
        <span className="flex-1 font-medium">{m.away.name}</span>
        {p && (
          <span className="text-xs text-slate-400 tabular-nums w-16 text-right">
            {p.expected_home_goals} - {p.expected_away_goals}
          </span>
        )}
      </div>
      {p && (
        <div className="flex items-center gap-3">
          <div className="flex-1 flex h-2 rounded-full overflow-hidden">
            {segs.map((s, i) => (
              <div key={i} className={s.color} style={{ width: `${s.v * 100}%` }} />
            ))}
          </div>
          <span className="text-xs text-slate-400 tabular-nums w-40 text-right">
            {(p.prob_home * 100).toFixed(0)}% / {(p.prob_draw * 100).toFixed(0)}% /{" "}
            {(p.prob_away * 100).toFixed(0)}%
          </span>
        </div>
      )}
    </div>
  );
}
