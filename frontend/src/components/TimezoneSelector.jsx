import { Globe } from "lucide-react";
import { TIMEZONES } from "../hooks/useTimezone.js";

export default function TimezoneSelector({ selected, onChange }) {
  return (
    <div className="flex items-center gap-2">
      <Globe size={14} className="text-slate-400" />
      <select
        value={selected.label}
        onChange={(e) => {
          const tz = TIMEZONES.find((t) => t.label === e.target.value);
          if (tz) onChange(tz);
        }}
        className="bg-white/5 border border-white/10 rounded-lg px-2 py-1 text-xs text-slate-300 focus:outline-none focus:ring-1 focus:ring-accent"
      >
        {TIMEZONES.map((tz) => (
          <option key={tz.label} value={tz.label}>
            {tz.label}
          </option>
        ))}
      </select>
    </div>
  );
}
