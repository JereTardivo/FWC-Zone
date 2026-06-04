import { useEffect, useState } from "react";
import { api } from "../api.js";
import { Loader2, MapPin, Users } from "lucide-react";
import Flag from "./Flag.jsx";

const COUNTRY_NAMES = {
  USA: "Estados Unidos",
  CAN: "Canadá",
  MEX: "México",
};

export default function Venues() {
  const [venues, setVenues] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    api
      .venues()
      .then((d) => {
        setVenues(d);
        setLoading(false);
      })
      .catch((e) => {
        setError(e.message);
        setLoading(false);
      });
  }, []);

  if (loading)
    return (
      <div className="flex items-center gap-2 text-slate-400">
        <Loader2 className="animate-spin" size={18} /> Cargando sedes...
      </div>
    );

  if (error)
    return (
      <div className="card p-4 border-red-500/30 text-red-300 text-sm">
        No se pudieron cargar las sedes: {error}
      </div>
    );

  const byCountry = venues.reduce((acc, v) => {
    (acc[v.country] = acc[v.country] || []).push(v);
    return acc;
  }, {});

  const countries = ["USA", "CAN", "MEX"];

  return (
    <div className="space-y-6">
      {countries.map((code) => {
        const list = byCountry[code] || [];
        if (list.length === 0) return null;
        return (
          <section key={code}>
            <h2 className="flex items-center gap-2 text-lg font-bold mb-3">
              <Flag
                teamId={code}
                className="w-6 h-4 rounded-sm ring-1 ring-white/10"
              />
              {COUNTRY_NAMES[code]}
              <span className="text-xs font-normal text-slate-400 ml-1">
                ({list.length} sedes)
              </span>
            </h2>
            <div className="grid gap-3 sm:grid-cols-2 lg:grid-cols-3">
              {list.map((v) => (
                <div
                  key={v.id}
                  className="card p-4 flex flex-col gap-2 hover:bg-white/5 transition"
                >
                  <div className="flex items-start justify-between gap-2">
                    <div>
                      <h3 className="font-semibold text-sm">{v.stadium}</h3>
                      <p className="text-xs text-slate-400">{v.city}</p>
                    </div>
                    <span className="text-[10px] px-2 py-0.5 rounded-full bg-white/10 text-slate-300 shrink-0">
                      {v.role}
                    </span>
                  </div>
                  <div className="flex items-center gap-4 text-xs text-slate-400 mt-1">
                    <span className="flex items-center gap-1">
                      <Users size={12} />
                      {v.capacity.toLocaleString()}
                    </span>
                    <span className="flex items-center gap-1">
                      <MapPin size={12} />
                      {v.country}
                    </span>
                  </div>
                </div>
              ))}
            </div>
          </section>
        );
      })}
    </div>
  );
}
