import { Apps } from "@/components/Apps";
import { Freshness } from "@/components/Freshness";
import { Panel, Rows } from "@/components/Panel";
import { Slab } from "@/components/Slab";
import { StatusGauge } from "@/components/StatusGauge";
import { Switches } from "@/components/Switches";
import { ThemeToggle } from "@/components/ThemeToggle";
import { type InfraSnapshot, severityTone, type Status, ZBX_SEVERITY } from "@/lib/infra";
import { useInfra } from "@/lib/useInfra";
import { useTheme } from "@/lib/useTheme";

const HEADLINE: Record<Status, string> = {
  ok: "Nominal",
  warn: "Degraded",
  crit: "Critical",
  unknown: "No signal",
};

function summary(s: InfraSnapshot): string {
  const bits = [`${s.containers.up}/${s.containers.total} up`];
  if (s.alerts.n) bits.push(`${s.alerts.n} alert${s.alerts.n === 1 ? "" : "s"}`);
  if (s.updates.n) bits.push(`${s.updates.n} update${s.updates.n === 1 ? "" : "s"}`);
  if (s.units_failed.length) bits.push(`${s.units_failed.length} unit failed`);
  return bits.join(" · ");
}

export function App() {
  const { surface, toggle } = useTheme();
  const { data, error, loading } = useInfra();
  const snap = data?.snapshot;

  return (
    <div className="mx-auto max-w-5xl px-6 pt-10 pb-16">
      <header className="flex items-center gap-4 border-b border-line pb-3">
        <span className="font-display text-base font-bold tracking-[0.22em] uppercase">
          clockmost
        </span>
        <span className="ef-label hidden sm:block">{"// console"}</span>
        <span className="flex-1" />
        {data ? <Freshness ageSeconds={data.age_seconds} stale={data.stale} /> : null}
        <ThemeToggle surface={surface} onToggle={toggle} />
      </header>
      <div className="ef-rule--tri" style={{ height: 2 }} />

      <main className="mt-8 flex flex-col gap-8">
        <Apps />

        {snap ? (
          <Slab
            kicker="// SYSTEM"
            headline={HEADLINE[snap.status]}
            detail={summary(snap)}
            watermark="CLOCKMOST"
          />
        ) : error ? (
          <p className="ef-mono text-sm text-magenta">/api/infra unreachable — {error.message}</p>
        ) : loading ? (
          <p className="ef-mono text-sm text-ink-3">reading snapshot…</p>
        ) : null}

        <div className="grid gap-3 lg:grid-cols-2">
          <Switches />

          {snap ? (
            <>
              <Panel
                idx="SEC.02"
                title="Deploy"
                note={snap.deploy.rollback_recent ? "rolled back" : undefined}
              >
                <div className="ef-statrow">
                  <span className="ef-statrow__k">commit</span>
                  <span className="ef-statrow__v">{snap.deploy.commit.split(" ")[0] || "—"}</span>
                </div>
                <p className="ef-mono text-xs text-ink-2">{snap.deploy.last || "—"}</p>
              </Panel>

              <Panel
                idx="SEC.03"
                title="Containers"
                note={`${snap.containers.up}/${snap.containers.total}`}
              >
                <Rows
                  items={[
                    ...snap.containers.down.map((c) => `${c} — down`),
                    ...snap.containers.unhealthy.map((c) => `${c} — unhealthy`),
                  ]}
                  tone="crit"
                  empty="all green"
                />
              </Panel>

              <Panel idx="SEC.04" title="Disk">
                <div className="flex items-center gap-6">
                  <StatusGauge value={snap.disk.root} label="root" unit="%" />
                  <StatusGauge value={snap.disk.home} label="home" unit="%" />
                </div>
              </Panel>

              <Panel idx="SEC.05" title="Alerts" note={`Zabbix · ${snap.alerts.n}`}>
                <Rows
                  items={snap.alerts.list.map((a) => `[${ZBX_SEVERITY[a.s] ?? a.s}] ${a.n}`)}
                  tone={severityTone(snap.alerts.max_sev)}
                  empty="no problems"
                />
              </Panel>

              <Panel idx="SEC.06" title="Updates" note={`Renovate · ${snap.updates.n}`}>
                <Rows
                  items={snap.updates.list.map((p) => `#${p.n} ${p.t}`)}
                  tone="warn"
                  empty="none pending"
                />
              </Panel>

              <Panel idx="SEC.07" title="Notifications" note="ntfy · clockmost">
                {snap.notify.list.length === 0 ? (
                  <p className="ef-mono text-xs text-ink-3">quiet</p>
                ) : (
                  <ul className="flex flex-col gap-2">
                    {snap.notify.list.map((n) => (
                      <li key={`${n.t}:${n.m}`} className="flex flex-col">
                        <span
                          className={`ef-mono text-xs ${n.p >= 4 ? "text-magenta" : n.p >= 3 ? "text-ink" : "text-ink-3"}`}
                        >
                          {n.ti}
                        </span>
                        <span className="ef-mono text-[0.6875rem] text-ink-3">{n.m}</span>
                      </li>
                    ))}
                  </ul>
                )}
              </Panel>

              {snap.units_failed.length > 0 ? (
                <Panel idx="SEC.08" title="Failed units">
                  <Rows items={snap.units_failed} tone="crit" empty="" />
                </Panel>
              ) : null}
            </>
          ) : null}
        </div>
      </main>
    </div>
  );
}
