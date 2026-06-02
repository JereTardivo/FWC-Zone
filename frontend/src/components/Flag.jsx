import { useState } from "react";
import { flagUrl } from "../utils.js";

export default function Flag({ teamId, className = "" }) {
  const [failed, setFailed] = useState(false);
  const url = flagUrl(teamId, 40);

  if (!url || failed) {
    return (
      <span
        className={`inline-grid place-items-center bg-white/10 text-[8px] font-bold text-slate-300 ${className}`}
      >
        {teamId}
      </span>
    );
  }

  return (
    <img
      src={url}
      srcSet={`${flagUrl(teamId, 80)} 2x`}
      alt={teamId}
      loading="lazy"
      onError={() => setFailed(true)}
      className={`object-cover ${className}`}
    />
  );
}
