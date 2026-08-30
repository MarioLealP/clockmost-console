import { Panel } from "@/components/Panel";
import { useApps } from "@/lib/useApps";

const GROUP_LABEL: Record<string, string> = {
  apps: "apps",
  streams: "twitch",
  ops: "ops",
};

export function Apps() {
  const { apps } = useApps();
  if (apps.length === 0) {
    return null;
  }

  const groups = [...new Set(apps.map((a) => a.group))];

  return (
    <Panel idx="SEC.00" title="Launch">
      <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
        {groups.map((g) => (
          <div key={g}>
            <p className="ef-label mb-2">{GROUP_LABEL[g] ?? g}</p>
            <div className="flex flex-wrap gap-2">
              {apps
                .filter((a) => a.group === g)
                .map((a) => (
                  <a key={a.url} href={a.url} target="_blank" rel="noreferrer" className="ef-btn">
                    {a.name}
                  </a>
                ))}
            </div>
          </div>
        ))}
      </div>
    </Panel>
  );
}
