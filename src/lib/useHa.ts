import useSWR from "swr";

import type { Switchable } from "./ha";

const DISABLED = "disabled" as const;
type Result = Switchable[] | typeof DISABLED;

async function fetcher(url: string): Promise<Result> {
  const res = await fetch(url, { headers: { accept: "application/json" } });
  if (res.status === 503) return DISABLED; // HA not configured — hide the panel
  if (!res.ok) throw new Error(`${url} → ${res.status}`);
  return (await res.json()) as Switchable[];
}

export function useHa() {
  const { data, mutate, isLoading } = useSWR<Result>("/api/ha/switches", fetcher, {
    refreshInterval: 10_000,
    revalidateOnFocus: false,
    revalidateOnMount: true,
    shouldRetryOnError: false,
  });

  const loading = isLoading && data === undefined;
  const enabled = data !== DISABLED;
  const switches = Array.isArray(data) ? data : [];

  async function toggle(entityId: string): Promise<void> {
    void mutate(
      (cur) =>
        Array.isArray(cur)
          ? cur.map((s) =>
              s.entity_id === entityId ? { ...s, state: s.state === "on" ? "off" : "on" } : s,
            )
          : cur,
      { revalidate: false },
    );
    try {
      await fetch(`/api/ha/${entityId}/toggle`, { method: "POST" });
    } finally {
      void mutate();
    }
  }

  return { switches, enabled, loading, toggle };
}
