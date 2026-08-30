import { Panel } from "@/components/Panel";
import { useHa } from "@/lib/useHa";

export function Switches() {
  const { switches, enabled, loading, toggle } = useHa();

  if (!loading && !enabled) {
    return null;
  }

  return (
    <Panel idx="SEC.00" title="Switches" note="home assistant">
      {loading ? (
        <p className="ef-mono text-xs text-ink-3">…</p>
      ) : switches.length === 0 ? (
        <p className="ef-mono text-xs text-ink-3">none configured</p>
      ) : (
        <ul className="flex flex-col gap-3">
          {switches.map((s) => (
            <li key={s.entity_id} className="flex items-center gap-3">
              <label className="ef-toggle">
                <input
                  type="checkbox"
                  checked={s.state === "on"}
                  onChange={() => void toggle(s.entity_id)}
                  aria-label={s.name}
                />
                <span />
              </label>
              <span className="ef-mono text-sm">{s.name}</span>
              <span className="ef-label ml-auto self-center">{s.state}</span>
            </li>
          ))}
        </ul>
      )}
    </Panel>
  );
}
