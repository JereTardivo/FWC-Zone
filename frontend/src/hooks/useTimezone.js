import { useState, useEffect, useCallback } from "react";

const STORAGE_KEY = "fwc_timezone";

export const TIMEZONES = [
  { label: "Argentina (UTC-3)", offset: -3 },
  { label: "España (UTC+2)", offset: 2 },
  { label: "Local (sede del partido)", offset: null },
  { label: "UTC", offset: 0 },
  { label: "México CDMX (UTC-6)", offset: -6 },
  { label: "USA Este (UTC-4)", offset: -4 },
  { label: "USA Oeste (UTC-7)", offset: -7 },
];

export function useTimezone() {
  const [selected, setSelected] = useState(() => {
    const saved = localStorage.getItem(STORAGE_KEY);
    if (saved) {
      const parsed = JSON.parse(saved);
      const found = TIMEZONES.find((t) => t.label === parsed.label);
      if (found) return found;
    }
    // Default: Argentina
    return TIMEZONES[0];
  });

  useEffect(() => {
    localStorage.setItem(STORAGE_KEY, JSON.stringify(selected));
  }, [selected]);

  const convertTime = useCallback(
    (timeStr, venueUtcOffset) => {
      if (!timeStr) return timeStr;
      if (selected.offset === null) {
        // Local mode: return original time
        return timeStr;
      }
      const [h, min] = timeStr.split(":").map(Number);
      const matchHour = h + min / 60;
      const venueOffset = venueUtcOffset ?? -5;
      const targetOffset = selected.offset;
      const utcHour = matchHour - venueOffset;
      const targetHour = utcHour + targetOffset;
      const totalMinutes = Math.round(targetHour * 60);
      const hh = Math.floor(totalMinutes / 60) % 24;
      const mm = totalMinutes % 60;
      return `${String(hh).padStart(2, "0")}:${String(mm).padStart(2, "0")}`;
    },
    [selected]
  );

  return { selected, setSelected, convertTime };
}
