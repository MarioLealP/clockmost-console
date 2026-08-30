interface FreshnessProps {
  ageSeconds: number;
  stale: boolean;
}

function label(s: number): string {
  if (s >= 10 ** 8) return "no data";
  if (s < 60) return `${s}s ago`;
  if (s < 3600) return `${Math.floor(s / 60)}m ago`;
  return `${Math.floor(s / 3600)}h ago`;
}

export function Freshness({ ageSeconds, stale }: FreshnessProps) {
  return (
    <span className="ef-pill" data-state={stale ? "warn" : "ok"}>
      <span className="ef-diamond" />
      {stale ? "stale" : "live"} · {label(ageSeconds)}
    </span>
  );
}
