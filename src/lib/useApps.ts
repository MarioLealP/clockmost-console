import useSWR from "swr";

import type { AppLink } from "./apps";

async function fetcher(url: string): Promise<AppLink[]> {
  const res = await fetch(url, { headers: { accept: "application/json" } });
  if (!res.ok) {
    throw new Error(`${url} → ${res.status}`);
  }
  return (await res.json()) as AppLink[];
}

export function useApps() {
  const { data } = useSWR<AppLink[]>("/api/apps", fetcher, {
    refreshInterval: 300_000, // the list barely changes
    revalidateOnFocus: false,
  });
  return { apps: data ?? [] };
}
