import type { ReactNode } from "react";

interface PanelProps {
  idx: string;
  title: string;
  note?: string;
  children: ReactNode;
}

export function Panel({ idx, title, note, children }: PanelProps) {
  return (
    <section className="ef-panel flex flex-col gap-3">
      <div className="ef-sec-head">
        <span className="ef-idx">{idx}</span>
        <h3>{title}</h3>
        {note ? <span className="ef-label ml-auto self-center">{note}</span> : null}
      </div>
      {children}
    </section>
  );
}

interface RowsProps {
  items: readonly string[];
  tone?: "dim" | "warn" | "crit";
  empty: string;
}

/** a plain mono list — the default body for the "nothing wrong" case */
export function Rows({ items, tone = "dim", empty }: RowsProps) {
  if (items.length === 0) {
    return <p className="ef-mono text-xs text-ink-3">{empty}</p>;
  }
  const color = tone === "crit" ? "text-magenta" : tone === "warn" ? "text-yellow" : "text-ink-2";
  return (
    <ul className="flex flex-col gap-1">
      {items.map((it) => (
        <li key={it} className={`ef-mono text-xs ${color}`}>
          {it}
        </li>
      ))}
    </ul>
  );
}
