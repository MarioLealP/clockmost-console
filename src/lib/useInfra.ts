import useSWR from "swr";

import type { InfraOut } from "./infra";

async function fetcher(url: string): Promise<InfraOut> {
  const res = await fetch(url, { headers: { accept: "application/json" } });
  if (!res.ok) {
    throw new Error(`${url} → ${res.status}`);
  }
  return (await res.json()) as InfraOut;
}

export function useInfra() {
  const { data, error, isLoading } = useSWR<InfraOut>("/api/infra", fetcher, {
    refreshInterval: 15_000,
    keepPreviousData: true,
    revalidateOnFocus: true,
  });

  return {
    data,
    error: error as Error | undefined,
    loading: isLoading && data === undefined,
  };
}
