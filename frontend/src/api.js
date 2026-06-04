const BASE = "/api";

async function getJSON(url) {
  const res = await fetch(url);
  if (!res.ok) throw new Error(`HTTP ${res.status}`);
  return res.json();
}

export const api = {
  teams: () => getJSON(`${BASE}/teams`),
  tournament: () => getJSON(`${BASE}/tournament`),
  venues: () => getJSON(`${BASE}/venues`),
  form: () => getJSON(`${BASE}/form`),
  team: (id) => getJSON(`${BASE}/team/${id}`),
  fixtures: () => getJSON(`${BASE}/fixtures`),
  simulate: (iterations = 5000) => getJSON(`${BASE}/simulate?iterations=${iterations}`),
  predict: async (home, away, neutral = true) => {
    const res = await fetch(`${BASE}/predict`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ home, away, neutral }),
    });
    if (!res.ok) throw new Error(`HTTP ${res.status}`);
    return res.json();
  },
};
