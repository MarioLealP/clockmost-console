import { useState } from "react";

import { DataStrip } from "@/components/DataStrip";
import { ServiceCard, type Health } from "@/components/ServiceCard";
import { Slab } from "@/components/Slab";
import { StatusGauge } from "@/components/StatusGauge";
import { TaskRow } from "@/components/TaskRow";
import { ThemeToggle } from "@/components/ThemeToggle";
import { useTheme } from "@/lib/useTheme";

interface Service {
  name: string;
  meta: string;
  health: Health;
  detail: string;
}

const SERVICES: readonly Service[] = [
  { name: "caddy", meta: "edge // 80 · 443", health: "ok", detail: "wildcard TLS · 15 routes" },
  { name: "authentik", meta: "auth // oidc", health: "ok", detail: "server + worker + pg16" },
  { name: "immich", meta: "photos // 2333", health: "ok", detail: "ml online · 41k assets" },
  { name: "factorio", meta: "game // 34197/udp", health: "warn", detail: "autosave 28h stale" },
  { name: "zabbix", meta: "monitor // 10051", health: "ok", detail: "0 problems" },
  { name: "gitea-runner", meta: "ci // act", health: "crit", detail: "runner offline" },
];

const STRIP: readonly string[] = [
  "NODE clockmost",
  "PWR 82.4%",
  "STACKS 6",
  "BACKUP full · rc=0",
  "RESTIC 44 snap · clean",
  "DEPLOY last-ok 3m",
  "SECTOR CLEAR",
];

export function App() {
  const { surface, toggle } = useTheme();
  const [checkStarted, setCheckStarted] = useState(false);

  return (
    <div className="mx-auto max-w-5xl px-6 pt-10 pb-16">
      <header className="flex items-center gap-4 border-b border-line pb-3">
        <span className="font-display text-base font-bold tracking-[0.22em] uppercase">
          clockmost
        </span>
        <span className="ef-label hidden sm:block">{"// console"}</span>
        <span className="flex-1" />
        <span className="ef-pill" data-state="ok">
          <span className="ef-diamond" />
          nominal
        </span>
        <ThemeToggle surface={surface} onToggle={toggle} />
      </header>
      <div className="ef-rule--tri" style={{ height: 2 }} />

      <main className="mt-8 flex flex-col gap-8">
        <Slab
          kicker="// SYSTEM"
          headline="Nominal"
          detail="6 stacks · 1 alert"
          watermark="CLOCKMOST"
        />

        <section>
          <div className="ef-sec-head mb-5">
            <span className="ef-idx">SEC.01</span>
            <h2>Services</h2>
          </div>
          <div className="grid gap-3 sm:grid-cols-2 lg:grid-cols-3">
            {SERVICES.map((service) => (
              <ServiceCard key={service.name} {...service} />
            ))}
          </div>
        </section>

        <section>
          <div className="ef-sec-head mb-5">
            <span className="ef-idx">SEC.02</span>
            <h2>Readings</h2>
          </div>
          <div className="flex flex-wrap items-center gap-6">
            <StatusGauge value={67} label="pwr" />
            <StatusGauge value={9} label="disk" unit="%" />
            <StatusGauge value={42} label="cpu" />
          </div>
        </section>

        <section>
          <div className="ef-sec-head mb-5">
            <span className="ef-idx">SEC.03</span>
            <h2>Queue</h2>
          </div>
          <div className="flex flex-col gap-1">
            {checkStarted ? (
              <TaskRow title="Weekly restic check" state="active" progress={0.15} meta="running" />
            ) : (
              <TaskRow
                title="Weekly restic check"
                state="ready"
                onRun={() => {
                  setCheckStarted(true);
                }}
              />
            )}
            <TaskRow
              title="Renovate PR sweep — 3 / 6"
              state="active"
              progress={0.5}
              meta="running"
            />
            <TaskRow title="Nightly full backup — done (rc=0)" state="done" meta="04:05" />
          </div>
        </section>
      </main>

      <DataStrip items={STRIP} />
    </div>
  );
}
