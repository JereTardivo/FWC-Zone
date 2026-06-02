export const CONF_COLORS = {
  UEFA: "bg-blue-500/15 text-blue-300",
  CONMEBOL: "bg-yellow-500/15 text-yellow-300",
  CONCACAF: "bg-red-500/15 text-red-300",
  CAF: "bg-emerald-500/15 text-emerald-300",
  AFC: "bg-purple-500/15 text-purple-300",
  OFC: "bg-cyan-500/15 text-cyan-300",
};

export function confBadge(conf) {
  return CONF_COLORS[conf] || "bg-white/10 text-slate-300";
}

export function pct(n) {
  return `${(n ?? 0).toFixed(1)}%`;
}
