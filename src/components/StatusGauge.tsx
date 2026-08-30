import type { CSSProperties } from "react";

interface StatusGaugeProps {
  /** 0–100; values outside are clamped. */
  value: number;
  label: string;
  /** small superscript after the number, e.g. "%". */
  unit?: string;
}

function clamp(n: number): number {
  return Math.max(0, Math.min(100, Math.round(n)));
}

/** The Endfield radial gauge (`.ef-gauge`) — a conic ring plus a centre metric. */
export function StatusGauge({ value, label, unit }: StatusGaugeProps) {
  const v = clamp(value);
  return (
    <div className="ef-gauge" style={{ "--ef-gauge-v": v } as CSSProperties}>
      <span className="ef-gauge__v">
        {v}
        {unit ? <span className="text-[0.5em]">{unit}</span> : null}
      </span>
      <span className="ef-gauge__l">{label}</span>
    </div>
  );
}
