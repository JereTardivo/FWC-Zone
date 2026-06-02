import { useEffect, useState } from "react";
import { api } from "../api.js";
import { Loader2, GitBranch } from "lucide-react";

const DAY_NAMES = ["Dom", "Lun", "Mar", "Mié", "Jue", "Vie", "Sáb"];

function fmtDate(iso) {
  const d = new Date(iso + "T00:00:00");
  return `${DAY_NAMES[d.getDay()]} ${String(d.getDate()).padStart(2, "0")}/${String(
    d.getMonth() + 1
  ).padStart(2, "0")}`;
}

const ROUNDS = [
  { key: "R32", title: "Dieciseisavos de final" },
  { key: "R16", title: "Octavos de final" },
  { key: "QF", title: "Cuartos de final" },
  { key: "SF", title: "Semifinales" },
  { key: "THIRD", title: "Tercer puesto" },
  { key: "FINAL", title: "Final" },
];

export default function Bracket() {
  const [knockout, setKnockout] = useState(null);
  const [error, setError] = useState(null);

  useEffect(() => {
    api
      .tournament()
      .then((d) => setKnockout(d.knockout || {}))
      .catch((e) => setError(e.message));
  }, []);

  if (error)
    return (
      <div className="card p-4 border-red-500/30 text-red-300 text-sm">
        No se pudo cargar las llaves: {error}
      </div>
    );
  if (!knockout)
    return (
      <div className="flex items-center gap-2 text-slate-400">
        <Loader2 className="animate-spin" size={18} /> Cargando llaves...
      </div>
    );

  const rounds = ROUNDS.filter((r) => (knockout[r.key] || []).length > 0);

  return (
    <div>
      <div className="flex items-center gap-2 mb-1">
        <GitBranch size={18} className="text-accent" />
        <h2 className="font-semibold">Cuadro de la fase final</h2>
      </div>
      <p className="text-sm text-slate-400 mb-5">
        Los participantes se definen al avanzar cada ronda. El motor resuelve los cruces
        automáticamente en la simulación. Las probabilidades por ronda están en{" "}
        <span className="text-accent">Simulación Monte Carlo</span>.
      </p>

      {rounds.length === 0 ? (
        <div className="card p-6 text-center text-slate-400 text-sm">
          Todavía no hay schedule de fase final cargado.
        </div>
      ) : (
        <div className="space-y-8">
          {rounds.map((r) => (
            <RoundBlock key={r.key} title={r.title} matches={knockout[r.key]} />
          ))}
        </div>
      )}
    </div>
  );
}

function RoundBlock({ title, matches }) {
  const byDate = {};
  for (const m of matches) (byDate[m.date] = byDate[m.date] || []).push(m);
  const isFinal = title === "Final";

  return (
    <section>
      <div className="flex items-center gap-2 mb-3">
        <h3 className={`font-semibold ${isFinal ? "text-amber-300" : "text-slate-200"}`}>
          {title}
        </h3>
        <span className="text-xs text-slate-500">({matches.length})</span>
      </div>
      <div className="space-y-4">
        {Object.entries(byDate).map(([date, ms]) => (
          <div key={date}>
            <div className="text-xs font-medium text-accent mb-2">{fmtDate(date)}</div>
            <div className="grid sm:grid-cols-2 gap-2">
              {ms.map((m) => (
                <div
                  key={m.match}
                  className={`card p-3 flex items-center gap-3 ${
                    isFinal ? "glow border-amber-300/30" : ""
                  }`}
                >
                  <span className="text-xs text-slate-500 w-12 tabular-nums">{m.time}</span>
                  <span className="text-[10px] px-1.5 py-0.5 rounded bg-white/10 text-slate-400">
                    #{m.match}
                  </span>
                  <span className="flex-1 text-sm font-medium">{m.label}</span>
                </div>
              ))}
            </div>
          </div>
        ))}
      </div>
    </section>
  );
}
