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

// Mapa código FIFA -> ISO 3166-1 alpha-2 (para banderas via flagcdn).
export const FIFA_TO_ISO2 = {
  ARG: "ar", FRA: "fr", ESP: "es", ENG: "gb-eng", BRA: "br", POR: "pt",
  NED: "nl", BEL: "be", GER: "de", CRO: "hr", URU: "uy", COL: "co",
  MAR: "ma", USA: "us", MEX: "mx", SUI: "ch", JPN: "jp", SEN: "sn",
  AUT: "at", KOR: "kr", ECU: "ec", CAN: "ca", AUS: "au", EGY: "eg",
  CIV: "ci", IRN: "ir", TUN: "tn", PAR: "py", SCO: "gb-sct", NOR: "no",
  QAT: "qa", SAU: "sa", GHA: "gh", PAN: "pa", ALG: "dz", UZB: "uz",
  JOR: "jo", RSA: "za", CPV: "cv", NZL: "nz", CZE: "cz", SWE: "se",
  TUR: "tr", COD: "cd", BIH: "ba", IRQ: "iq", HAI: "ht", CUW: "cw",
};

export function flagUrl(teamId, width = 40) {
  const iso = FIFA_TO_ISO2[teamId];
  return iso ? `https://flagcdn.com/w${width}/${iso}.png` : null;
}
