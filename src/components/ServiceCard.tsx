export type Health = "ok" | "warn" | "crit";

interface ServiceCardProps {
  name: string;
  meta: string;
  health: Health;
  detail?: string;
}

const HEALTH_LABEL: Record<Health, string> = {
  ok: "Nominal",
  warn: "Degraded",
  crit: "Down",
};

export function ServiceCard({ name, meta, health, detail }: ServiceCardProps) {
  return (
    <div className="ef-card ef-brackets">
      <div className="ef-card__head">
        <span className="ef-diamond" data-active={health === "ok" ? "" : undefined} />
        <div>
          <div className="ef-card__title">{name}</div>
          <div className="ef-card__meta">{meta}</div>
        </div>
      </div>
      {detail ? <p className="text-sm text-ink-2">{detail}</p> : null}
      <div className="mt-3">
        <span className="ef-pill" data-state={health}>
          <span className="ef-diamond" />
          {HEALTH_LABEL[health]}
        </span>
      </div>
    </div>
  );
}
