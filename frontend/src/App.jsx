import { useState } from "react";
import { Trophy, Grid3x3, Cpu, CalendarDays, GitBranch, MapPin } from "lucide-react";
import Groups from "./components/Groups.jsx";
import Simulation from "./components/Simulation.jsx";
import Calendar from "./components/Calendar.jsx";
import Bracket from "./components/Bracket.jsx";
import Venues from "./components/Venues.jsx";
import TeamDetail from "./components/TeamDetail.jsx";

const TABS = [
  { id: "groups", label: "Grupos", icon: Grid3x3 },
  { id: "calendar", label: "Calendario", icon: CalendarDays },
  { id: "bracket", label: "Llaves", icon: GitBranch },
  { id: "venues", label: "Sedes", icon: MapPin },
  { id: "simulate", label: "Simulación Monte Carlo", icon: Cpu },
];

export default function App() {
  const [tab, setTab] = useState("groups");
  const [selectedTeam, setSelectedTeam] = useState(null);

  return (
    <div className="max-w-6xl mx-auto px-4 py-8">
      <header className="flex items-center gap-3 mb-2">
        <div className="p-2 rounded-xl bg-accent/15 text-accent glow">
          <Trophy size={28} />
        </div>
        <div>
          <h1 className="text-2xl md:text-3xl font-extrabold tracking-tight">
            Predictor <span className="text-accent">Mundial 2026</span>
          </h1>
          <p className="text-sm text-slate-400">
            Motor estadístico: Elo + Poisson + simulación Monte Carlo
          </p>
        </div>
      </header>

      <nav className="flex flex-wrap gap-2 my-6">
        {TABS.map(({ id, label, icon: Icon }) => (
          <button
            key={id}
            onClick={() => setTab(id)}
            className={`flex items-center gap-2 px-4 py-2 rounded-xl text-sm font-medium transition ${
              tab === id
                ? "bg-accent text-ink"
                : "bg-white/5 text-slate-300 hover:bg-white/10"
            }`}
          >
            <Icon size={16} />
            {label}
          </button>
        ))}
      </nav>

      <main>
        {selectedTeam ? (
          <TeamDetail teamId={selectedTeam} onBack={() => setSelectedTeam(null)} />
        ) : (
          <>
            {tab === "groups" && <Groups onSelectTeam={setSelectedTeam} />}
            {tab === "calendar" && <Calendar />}
            {tab === "bracket" && <Bracket />}
            {tab === "venues" && <Venues />}
            {tab === "simulate" && <Simulation />}
          </>
        )}
      </main>

      <footer className="mt-12 text-center text-xs text-slate-500">
        Datos seed editables · Reemplazá ratings y sorteo en{" "}
        <code className="text-slate-400">backend/app/data/</code>
      </footer>
    </div>
  );
}
