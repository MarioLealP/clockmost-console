export type TaskState = "ready" | "active" | "done";

interface TaskRowProps {
  title: string;
  state: TaskState;
  /** 0–1, drawn as the thin baseline bar when `state` is "active". */
  progress?: number;
  /** right-aligned mono note for "active" / "done". */
  meta?: string;
  onRun?: () => void;
}

export function TaskRow({ title, state, progress = 0, meta, onRun }: TaskRowProps) {
  const pct = Math.max(0, Math.min(100, Math.round(progress * 100)));

  return (
    <div className="ef-task" data-state={state}>
      <span className="ef-task__title">{title}</span>

      {state === "ready" && onRun ? (
        <button type="button" className="ef-btn ef-btn--primary" onClick={onRun}>
          Run
        </button>
      ) : (
        <span className="ef-mono ef-dim text-xs">{meta}</span>
      )}

      {state === "active" ? (
        <span className="ef-task__prog">
          <i style={{ width: `${pct}%` }} />
        </span>
      ) : null}
    </div>
  );
}
