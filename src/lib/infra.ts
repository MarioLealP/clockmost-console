/** Mirrors backend `app/schemas.py` (which mirrors `clockmost-status`). */

export type Status = "ok" | "warn" | "crit" | "unknown";

export interface InfraSnapshot {
  status: Status;
  ts: number;
  deploy: { commit: string; last: string; rollback_recent: number };
  containers: { up: number; total: number; down: string[]; unhealthy: string[] };
  units_failed: string[];
  disk: { root: number; home: number };
  updates: { n: number; list: { n: number; t: string }[] };
  alerts: { n: number; max_sev: number; list: { s: number; n: string }[] };
  notify: { n: number; list: { t: number; ti: string; m: string; p: number }[] };
}

export interface HistoryPoint {
  ts: number;
  status: string;
  containers_up: number;
  containers_total: number;
  disk_root: number;
  disk_home: number;
  alerts_n: number;
  alerts_max_sev: number;
}

export interface InfraOut {
  snapshot: InfraSnapshot;
  stale: boolean;
  age_seconds: number;
  history: HistoryPoint[];
}

export const ZBX_SEVERITY = [
  "not classified",
  "information",
  "warning",
  "average",
  "high",
  "disaster",
] as const;

/** Zabbix severity 0–5 → an .ef status tone. */
export function severityTone(s: number): "dim" | "warn" | "crit" {
  if (s >= 4) return "crit";
  if (s >= 2) return "warn";
  return "dim";
}
