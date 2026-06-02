import { useEffect, useState } from "react";
import { api } from "../api.js";
import { confBadge } from "../utils.js";
import Flag from "./Flag.jsx";
import { Loader2 } from "lucide-react";

// Columnas de la tabla de posiciones (abreviatura + título descriptivo).
const COLS = [
  { key: "pj", label: "PJ", title: "Partidos jugados" },
  { key: "pg", label: "PG", title: "Partidos ganados" },
  { key: "pe", label: "PE", title: "Partidos empatados" },
  { key: "pp", label: "PP", title: "Partidos perdidos" },
  { key: "gf", label: "GF", title: "Goles a favor" },
  { key: "gc", label: "GC", title: "Goles en contra" },
  { key: "dif", label: "DIF", title: "Diferencia de goles" },
  { key: "pts", label: "PTS", title: "Puntos" },
];

// Genera la fila de posiciones de un equipo. Hoy en cero (torneo no iniciado);
// cuando se carguen resultados, estos valores vendrán calculados.
function toRow(team) {
  const s = team.stats || {};
  const pg = s.pg || 0;
  const pe = s.pe || 0;
  const pp = s.pp || 0;
  const gf = s.gf || 0;
  const gc = s.gc || 0;
  return {
    ...team,
    pj: s.pj ?? pg + pe + pp,
    pg,
    pe,
    pp,
    gf,
    gc,
    dif: s.dif ?? gf - gc,
    pts: s.pts ?? pg * 3 + pe,
  };
}

function standings(teams) {
  return teams
    .map(toRow)
    .sort(
      (a, b) =>
        b.pts - a.pts ||
        b.dif - a.dif ||
        b.gf - a.gf ||
        b.elo - a.elo
    );
}

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
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
        {Object.entries(data.groups).map(([gid, teams]) => (
          <GroupTable
            key={gid}
            gid={gid}
            rows={standings(teams)}
            onSelectTeam={onSelectTeam}
          />
        ))}
      </div>
      <p className="text-xs text-slate-500 mt-4 flex items-center gap-2">
        <span className="inline-block w-3 h-3 rounded-sm bg-accent/60" />
        Zona de clasificación (1° y 2° avanzan directo; mejores 3ros se definen
        entre grupos).
      </p>
    </div>
  );
}

function GroupTable({ gid, rows, onSelectTeam }) {
  return (
    <div className="card p-4">
      <div className="flex items-center gap-2 mb-3">
        <span className="w-7 h-7 rounded-lg bg-accent text-ink font-bold grid place-items-center text-sm">
          {gid}
        </span>
        <h3 className="font-semibold">Grupo {gid}</h3>
      </div>

      <div className="overflow-x-auto -mx-1">
        <table className="w-full text-sm border-collapse">
          <thead>
            <tr className="text-[10px] uppercase tracking-wide text-slate-500">
              <th className="text-left font-medium pb-2 pl-1 w-6">#</th>
              <th className="text-left font-medium pb-2">Equipo</th>
              {COLS.map((c) => (
                <th
                  key={c.key}
                  title={c.title}
                  className={`font-medium pb-2 w-7 text-center ${
                    c.key === "pts" ? "text-accent" : ""
                  }`}
                >
                  {c.label}
                </th>
              ))}
            </tr>
          </thead>
          <tbody>
            {rows.map((t, i) => {
              const qualifies = i < 2;
              return (
                <tr
                  key={t.id}
                  className="border-t border-white/5 hover:bg-white/5 transition cursor-pointer group"
                  onClick={() => onSelectTeam && onSelectTeam(t.id)}
                >
                  <td className="py-1.5 pl-1">
                    <span
                      className={`inline-grid place-items-center w-5 h-5 rounded text-[11px] tabular-nums ${
                        qualifies
                          ? "bg-accent/20 text-accent font-bold"
                          : "text-slate-500"
                      }`}
                    >
                      {i + 1}
                    </span>
                  </td>
                  <td className="py-1.5 pr-2">
                    <span className="flex items-center gap-2 min-w-0">
                      <Flag
                        teamId={t.id}
                        className="w-5 h-3.5 rounded-sm shrink-0 ring-1 ring-white/10"
                      />
                      <span className="truncate font-medium group-hover:text-accent transition">
                        {t.name}
                      </span>
                      {t.host && (
                        <span className="text-[9px] px-1 py-0.5 rounded bg-accent/20 text-accent shrink-0">
                          SEDE
                        </span>
                      )}
                      <span
                        className={`text-[9px] px-1 py-0.5 rounded shrink-0 ${confBadge(
                          t.confederation
                        )}`}
                      >
                        {t.confederation}
                      </span>
                    </span>
                  </td>
                  {COLS.map((c) => (
                    <td
                      key={c.key}
                      className={`py-1.5 text-center text-[11px] tabular-nums ${
                        c.key === "pts"
                          ? "font-bold text-slate-100"
                          : "text-slate-400"
                      }`}
                    >
                      {t[c.key]}
                    </td>
                  ))}
                </tr>
              );
            })}
          </tbody>
        </table>
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
