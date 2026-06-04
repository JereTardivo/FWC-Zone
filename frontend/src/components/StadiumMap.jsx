import { MapContainer, TileLayer, CircleMarker, Popup } from "react-leaflet";

const COLORS = {
  USA: "#3b82f6",
  CAN: "#ef4444",
  MEX: "#22c55e",
};

export default function StadiumMap({ venues }) {
  // centro aproximado del área de los 3 países
  const center = [37, -100];
  const zoom = 3;

  return (
    <div className="w-full h-96 rounded-2xl overflow-hidden border border-white/10">
      <MapContainer
        center={center}
        zoom={zoom}
        scrollWheelZoom={false}
        style={{ width: "100%", height: "100%" }}
      >
        <TileLayer
          url="https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png"
          attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors &copy; <a href="https://carto.com/">CARTO</a>'
        />
        {venues.map((v) => (
          <CircleMarker
            key={v.id}
            center={[v.lat, v.lng]}
            radius={6 + v.capacity / 15000}
            pathOptions={{
              color: COLORS[v.country] || "#94a3b8",
              fillColor: COLORS[v.country] || "#94a3b8",
              fillOpacity: 0.7,
              weight: 2,
            }}
          >
            <Popup>
              <div className="text-slate-800">
                <b>{v.stadium}</b>
                <br />
                <span className="text-sm">{v.city}, {v.country}</span>
                <br />
                <span className="text-xs text-slate-600">{v.role}</span>
                <br />
                <span className="text-xs text-slate-500">
                  {v.capacity.toLocaleString()} espectadores
                </span>
              </div>
            </Popup>
          </CircleMarker>
        ))}
      </MapContainer>
    </div>
  );
}
