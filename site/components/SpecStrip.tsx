const stats = [
  { number: '8', label: 'Specialist Agents' },
  { number: '12', label: 'Reusable Skills' },
  { number: '8', label: 'Auto-Detected Domains' },
  { number: '60', label: 'Tests Passing' },
];

export default function SpecStrip() {
  return (
    <section className="bg-canvas-elevated border-y border-hairline py-xl px-xs">
      <div className="max-w-editorial mx-auto grid grid-cols-2 md:grid-cols-4 gap-px bg-hairline border border-hairline overflow-hidden">
        {stats.map(({ number, label }) => (
          <div key={label} className="bg-canvas-elevated px-md py-lg flex flex-col items-center text-center">
            <span
              className="text-ink block"
              style={{ fontSize: 'clamp(48px, 6vw, 80px)', fontWeight: 700, lineHeight: 1.0, letterSpacing: '-1.6px' }}
            >
              {number}
            </span>
            <span
              className="text-muted mt-xxs block"
              style={{ fontSize: '11px', fontWeight: 600, letterSpacing: '1.1px', textTransform: 'uppercase' }}
            >
              {label}
            </span>
          </div>
        ))}
      </div>
    </section>
  );
}
