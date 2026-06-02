import { useEffect, useState } from "react";
import { api } from "../api.js";
import { Loader2, Swords } from "lucide-react";

export default function MatchPredictor() {
  const [teams, setTeams] = useState([]);
  const [home, setHome] = useState("ARG");
  const [away, setAway] = useState("BRA");
  const [neutral, setNeutral] = useState(true);
  const [pred, setPred] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  useEffect(() => {
    api.teams().then((t) => setTeams(t.sort((a, b) => a.name.localeCompare(b.name))));
  }, []);

  async function run() {
    if (home === away) {
      setError("Elegí dos equipos distintos");
      return;
    }
    setError(null);
    setLoading(true);
    try {
      setPred(await api.predict(home, away, neutral));
    } catch (e) {
      setError(e.message);
    } finally {
      setLoading(false);
    }
  }

  const nameOf = (id) => teams.find((t) => t.id === id)?.name || id;

  return (
    <div className="grid lg:grid-cols-2 gap-6">
      <div className="card p-5">
        <h3 className="font-semibold mb-4 flex items-center gap-2">
          <Swords size={18} className="text-accent" /> Configurar partido
        </h3>
        <div className="grid grid-cols-2 gap-3">
          <Select label="Local" value={home} onChange={setHome} teams={teams} />
          <Select label="Visitante" value={away} onChange={setAway} teams={teams} />
        </div>
        <label className="flex items-center gap-2 mt-4 text-sm text-slate-300">
          <input
            type="checkbox"
            checked={neutral}
            onChange={(e) => setNeutral(e.target.checked)}
            className="accent-accent"
          />
          Cancha neutral (sin ventaja de localía)
        </label>
        <button
          onClick={run}
          disabled={loading}
          className="mt-5 w-full bg-accent text-ink font-semibold py-2.5 rounded-xl hover:brightness-110 transition disabled:opacity-50 flex items-center justify-center gap-2"
        >
          {loading ? <Loader2 className="animate-spin" size={16} /> : null}
          Calcular probabilidades
        </button>
        {error && <p className="text-red-300 text-sm mt-3">{error}</p>}
      </div>

      <div className="card p-5">
        {!pred ? (
          <p className="text-slate-400 text-sm">
            Configurá un partido y calculá para ver el desglose probabilístico.
          </p>
        ) : (
          <Result pred={pred} nameOf={nameOf} />
        )}
      </div>
    </div>
  );
}

function Select({ label, value, onChange, teams }) {
  return (
    <label className="text-sm">
      <span className="text-slate-400">{label}</span>
      <select
        value={value}
        onChange={(e) => onChange(e.target.value)}
        className="mt-1 w-full bg-ink/60 border border-white/10 rounded-lg px-3 py-2 text-sm"
      >
        {teams.map((t) => (
          <option key={t.id} value={t.id}>
            {t.name}
          </option>
        ))}
      </select>
    </label>
  );
}

function Result({ pred, nameOf }) {
  const segs = [
    { label: nameOf(pred.home_id), v: pred.prob_home, color: "bg-accent" },
    { label: "Empate", v: pred.prob_draw, color: "bg-slate-400" },
    { label: nameOf(pred.away_id), v: pred.prob_away, color: "bg-blue-400" },
  ];
  return (
    <div>
      <div className="flex justify-between text-sm mb-1">
        {segs.map((s) => (
          <span key={s.label} className="text-slate-300">
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
        {pred.top_scorelines.map((s) => (
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
