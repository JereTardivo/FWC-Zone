import { useState } from "react";
import { api } from "../api.js";
import { confBadge, pct } from "../utils.js";
import { Cpu, Loader2, Trophy } from "lucide-react";
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  Tooltip,
  ResponsiveContainer,
  Cell,
} from "recharts";

const ITER_OPTIONS = [1000, 5000, 10000, 25000];

export default function Simulation() {
  const [iterations, setIterations] = useState(5000);
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  async function run() {
    setLoading(true);
    setError(null);
    try {
      setResult(await api.simulate(iterations));
    } catch (e) {
      setError(e.message);
    } finally {
      setLoading(false);
    }
  }

  const chartData =
    result?.teams
      .filter((t) => t.champion_pct > 0)
      .slice(0, 12)
      .map((t) => ({ name: t.name, value: t.champion_pct })) || [];

  return (
    <div>
      <div className="card p-5 mb-6">
        <h3 className="font-semibold mb-3 flex items-center gap-2">
          <Cpu size={18} className="text-accent" /> Simular torneo completo
        </h3>
        <p className="text-sm text-slate-400 mb-4">
          Cada iteración juega el Mundial entero (grupos + eliminatorias)
          muestreando goles con Poisson. Más iteraciones = más precisión.
        </p>
        <div className="flex flex-wrap items-center gap-3">
          <select
            value={iterations}
            onChange={(e) => setIterations(Number(e.target.value))}
            className="bg-ink/60 border border-white/10 rounded-lg px-3 py-2 text-sm"
          >
            {ITER_OPTIONS.map((n) => (
              <option key={n} value={n}>
                {n.toLocaleString()} simulaciones
              </option>
            ))}
          </select>
          <button
            onClick={run}
            disabled={loading}
            className="bg-accent text-ink font-semibold px-5 py-2 rounded-xl hover:brightness-110 transition disabled:opacity-50 flex items-center gap-2"
          >
            {loading ? <Loader2 className="animate-spin" size={16} /> : <Trophy size={16} />}
            {loading ? "Simulando..." : "Ejecutar"}
          </button>
        </div>
        {error && <p className="text-red-300 text-sm mt-3">{error}</p>}
      </div>

      {result && (
        <div className="grid lg:grid-cols-2 gap-6">
          <div className="card p-5">
            <h4 className="font-semibold mb-3">Probabilidad de campeón (top 12)</h4>
            <ResponsiveContainer width="100%" height={360}>
              <BarChart data={chartData} layout="vertical" margin={{ left: 20 }}>
                <XAxis type="number" stroke="#64748b" fontSize={11} unit="%" />
                <YAxis
                  type="category"
                  dataKey="name"
                  stroke="#94a3b8"
                  fontSize={11}
                  width={90}
                />
                <Tooltip
                  contentStyle={{
                    background: "#0f172a",
                    border: "1px solid rgba(255,255,255,0.1)",
                    borderRadius: 12,
                  }}
                  formatter={(v) => [`${v}%`, "Campeón"]}
                />
                <Bar dataKey="value" radius={[0, 6, 6, 0]}>
                  {chartData.map((_, i) => (
                    <Cell key={i} fill={i === 0 ? "#16c784" : "#0e8a5f"} />
                  ))}
                </Bar>
              </BarChart>
            </ResponsiveContainer>
          </div>

          <div className="card p-5 overflow-auto max-h-[420px]">
            <h4 className="font-semibold mb-3">
              Tabla completa ({result.iterations.toLocaleString()} sims)
            </h4>
            <table className="w-full text-sm">
              <thead className="text-slate-400 text-left sticky top-0 bg-ink/80 backdrop-blur">
                <tr>
                  <th className="py-2">#</th>
                  <th>Equipo</th>
                  <th className="text-right">🏆 Campeón</th>
                  <th className="text-right">Final</th>
                  <th className="text-right">Podio</th>
                  <th className="text-right">Avanza</th>
                </tr>
              </thead>
              <tbody>
                {result.teams.map((t, i) => (
                  <tr key={t.team_id} className="border-t border-white/5">
                    <td className="py-2 text-slate-500">{i + 1}</td>
                    <td>
                      <span className="flex items-center gap-2">
                        {t.name}
                        <span
                          className={`text-[10px] px-1.5 py-0.5 rounded ${confBadge(
                            t.confederation
                          )}`}
                        >
                          {t.confederation}
                        </span>
                      </span>
                    </td>
                    <td className="text-right tabular-nums font-semibold text-accent">
                      {pct(t.champion_pct)}
                    </td>
                    <td className="text-right tabular-nums text-slate-300">
                      {pct(t.final_pct)}
                    </td>
                    <td className="text-right tabular-nums text-amber-300">
                      {pct(t.podium_pct)}
                    </td>
                    <td className="text-right tabular-nums text-slate-400">
                      {pct(t.qualify_pct)}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}
    </div>
  );
}
