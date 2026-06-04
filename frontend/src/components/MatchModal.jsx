import { useEffect, useState } from "react";
import { api } from "../api.js";
import Flag from "./Flag.jsx";
import { Loader2, X, MapPin, Home } from "lucide-react";

// Anfitriones del Mundial 2026: solo ellos juegan con ventaja de localía.
const HOSTS = ["MEX", "USA", "CAN"];

export default function MatchModal({ match, onClose }) {
  const [pred, setPred] = useState(null);
  const [error, setError] = useState(null);

  // Localía solo si el local del fixture es anfitrión (México, EE.UU. o Canadá).
  const homeIsHost = HOSTS.includes(match.home.id);
  const neutral = !homeIsHost;

  useEffect(() => {
    setPred(null);
    setError(null);
    api
      .predict(match.home.id, match.away.id, neutral)
      .then(setPred)
      .catch((e) => setError(e.message));
  }, [match, neutral]);

  // Cerrar con Escape.
  useEffect(() => {
    const onKey = (e) => e.key === "Escape" && onClose();
    window.addEventListener("keydown", onKey);
    return () => window.removeEventListener("keydown", onKey);
  }, [onClose]);

  return (
    <div
      className="fixed inset-0 z-50 grid place-items-center bg-black/70 backdrop-blur-sm p-4"
      onClick={onClose}
    >
      <div
        className="card p-6 w-full max-w-lg relative"
        onClick={(e) => e.stopPropagation()}
      >
        <button
          onClick={onClose}
          className="absolute top-4 right-4 text-slate-400 hover:text-white transition"
        >
          <X size={18} />
        </button>

        {/* Cabecera del partido */}
        <div className="flex items-center justify-center gap-4 mb-1">
          <div className="flex items-center gap-2">
            <Flag teamId={match.home.id} className="w-7 h-5 rounded-sm ring-1 ring-white/10" />
            <span className="font-bold">{match.home.name}</span>
          </div>
          <span className="text-slate-500 text-sm">vs</span>
          <div className="flex items-center gap-2">
            <span className="font-bold">{match.away.name}</span>
            <Flag teamId={match.away.id} className="w-7 h-5 rounded-sm ring-1 ring-white/10" />
          </div>
        </div>
        <div className="flex items-center justify-center gap-2 text-xs text-slate-400 mb-5">
          {match.group && <span>Grupo {match.group}</span>}
          {match.time && <span>· {match.time}</span>}
          <span className="flex items-center gap-1">
            ·
            {neutral ? (
              <>
                <MapPin size={12} /> Cancha neutral
              </>
            ) : (
              <>
                <Home size={12} className="text-accent" />
                <span className="text-accent">Localía de {match.home.name}</span>
              </>
            )}
          </span>
          {match.venue && (
            <span className="flex items-center gap-1">
              · <MapPin size={12} /> {match.venue.stadium}, {match.venue.city}
            </span>
          )}
        </div>

        {error && (
          <p className="text-red-300 text-sm text-center py-6">
            No se pudo calcular: {error}
          </p>
        )}
        {!pred && !error && (
          <div className="flex items-center justify-center gap-2 text-slate-400 py-10">
            <Loader2 className="animate-spin" size={18} /> Calculando…
          </div>
        )}
        {pred && (
          <Result
            pred={pred}
            homeName={match.home.name}
            awayName={match.away.name}
          />
        )}
      </div>
    </div>
  );
}

function Result({ pred, homeName, awayName }) {
  const segs = [
    { label: homeName, v: pred.prob_home, color: "bg-accent" },
    { label: "Empate", v: pred.prob_draw, color: "bg-slate-400" },
    { label: awayName, v: pred.prob_away, color: "bg-blue-400" },
  ];

  return (
    <div>
      <div className="flex justify-between text-sm mb-1">
        {segs.map((s) => (
          <span key={s.label} className="text-slate-300 truncate max-w-[33%]">
            {s.label} <b>{(s.v * 100).toFixed(1)}%</b>
          </span>
        ))}
      </div>
      <div className="flex h-3 rounded-full overflow-hidden mb-5">
        {segs.map((s) => (
          <div key={s.label} className={s.color} style={{ width: `${s.v * 100}%` }} />
        ))}
      </div>

      <div className="grid grid-cols-2 gap-3 text-sm">
        <Stat label="Goles esperados (local)" value={pred.expected_home_goals} />
        <Stat label="Goles esperados (visita)" value={pred.expected_away_goals} />
        <Stat label="Over 2.5 goles" value={`${(pred.over_2_5 * 100).toFixed(0)}%`} />
        <Stat label="Ambos marcan" value={`${(pred.btts * 100).toFixed(0)}%`} />
      </div>

      <h4 className="text-sm font-semibold mt-5 mb-2 text-slate-300">
        Marcadores más probables
      </h4>
      <div className="grid grid-cols-3 gap-2">
        {(pred.top_scorelines || []).map((s) => (
          <div key={s.score} className="bg-white/5 rounded-lg px-3 py-2 text-center">
            <div className="font-bold tabular-nums">{s.score}</div>
            <div className="text-xs text-slate-400">{(s.prob * 100).toFixed(1)}%</div>
          </div>
        ))}
      </div>
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
