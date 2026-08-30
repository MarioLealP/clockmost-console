interface DataStripProps {
  items: readonly string[];
}

/** The fixed bottom telemetry strip — slow, linear, off under reduced motion. */
export function DataStrip({ items }: DataStripProps) {
  return (
    <div className="fixed inset-x-0 bottom-0 z-40 flex h-[22px] items-center overflow-hidden border-t border-line bg-ground">
      <div className="flex whitespace-nowrap motion-safe:animate-[ef-scan_44s_linear_infinite]">
        {(["a", "b"] as const).map((copy) => (
          <div key={copy} className="flex" aria-hidden={copy === "b"}>
            {items.map((item) => (
              <span key={item} className="ef-mono px-6 text-[0.6875rem] tracking-wide text-ink-4">
                {item}
              </span>
            ))}
          </div>
        ))}
      </div>
    </div>
  );
}
