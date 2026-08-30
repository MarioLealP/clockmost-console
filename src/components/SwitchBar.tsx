import { useHa } from "@/lib/useHa";

/**
 * Always-visible strip of Home Assistant toggles — sits above the tabs so the
 * switches are one click away from any view. Hides itself when HA is off or
 * nothing is configured.
 */
export function SwitchBar() {
  const { switches, enabled, loading, toggle } = useHa();

  if (!loading && (!enabled || switches.length === 0)) {
    return null;
  }

  return (
    <div className="ef-panel mt-6 flex flex-wrap items-center gap-x-8 gap-y-3">
      <span className="ef-label">home</span>

      {loading ? (
        <span className="ef-mono text-xs text-ink-3">…</span>
      ) : (
        switches.map((s) => (
          <label key={s.entity_id} className="flex cursor-pointer items-center gap-2.5">
            <span className="ef-toggle">
              <input
                type="checkbox"
                checked={s.state === "on"}
                onChange={() => void toggle(s.entity_id)}
                aria-label={s.name}
              />
              <span />
            </span>
            <span className="ef-mono text-sm">{s.name}</span>
            <span className="ef-label">{s.state}</span>
          </label>
        ))
      )}
    </div>
  );
}
