import { useEffect, useState } from "react";
import { api } from "../api.js";
import { confBadge } from "../utils.js";
import { Loader2, ShieldHalf } from "lucide-react";

export default function Groups({ onSelectTeam }) {
  const [data, setData] = useState(null);
  const [error, setError] = useState(null);

  useEffect(() => {
    api.tournament().then(setData).catch((e) => setError(e.message));
  }, []);

  if (error)
    return <ErrorBox msg={`No se pudo cargar el torneo: ${error}`} />;
  if (!data)
    return (
      <div className="flex items-center gap-2 text-slate-400">
        <Loader2 className="animate-spin" size={18} /> Cargando grupos...
      </div>
    );

  return (
    <div>
      <p className="text-sm text-slate-400 mb-4">{data.meta.format}</p>
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
        {Object.entries(data.groups).map(([gid, teams]) => (
          <div key={gid} className="card p-4">
            <div className="flex items-center gap-2 mb-3">
              <span className="w-7 h-7 rounded-lg bg-accent text-ink font-bold grid place-items-center text-sm">
                {gid}
              </span>
              <h3 className="font-semibold">Grupo {gid}</h3>
            </div>
            <ul className="space-y-2">
              {teams
                .slice()
                .sort((a, b) => b.elo - a.elo)
                .map((t) => (
                  <li key={t.id}>
                    <button
                      onClick={() => onSelectTeam && onSelectTeam(t.id)}
                      className="w-full flex items-center justify-between text-sm rounded-lg px-2 py-1 -mx-2 hover:bg-white/5 transition text-left"
                    >
                      <span className="flex items-center gap-2">
                        <ShieldHalf size={14} className="text-slate-500" />
                        {t.name}
                        {t.host && (
                          <span className="text-[10px] px-1.5 py-0.5 rounded bg-accent/20 text-accent">
                            SEDE
                          </span>
                        )}
                      </span>
                      <span className="flex items-center gap-2">
                        <span
                          className={`text-[10px] px-1.5 py-0.5 rounded ${confBadge(
                            t.confederation
                          )}`}
                        >
                          {t.confederation}
                        </span>
                        <span className="tabular-nums text-slate-400">
                          {Math.round(t.elo)}
                        </span>
                      </span>
                    </button>
                  </li>
                ))}
            </ul>
          </div>
        ))}
      </div>
    </div>
  );
}

function ErrorBox({ msg }) {
  return (
    <div className="card p-4 border-red-500/30 text-red-300 text-sm">
      {msg}
      <p className="text-slate-400 mt-1">
        ¿Está corriendo el backend en <code>localhost:8000</code>?
      </p>
    </div>
  );
}
