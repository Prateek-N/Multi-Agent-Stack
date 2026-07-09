'use client';

import { useEffect, useRef, useState } from 'react';

const stats = [
  { number: 8, label: 'Specialist Agents' },
  { number: 12, label: 'Reusable Skills' },
  { number: 8, label: 'Auto-Detected Domains' },
  { number: 60, label: 'Tests Passing' },
];

function prefersReducedMotion() {
  return (
    typeof window !== 'undefined' &&
    window.matchMedia?.('(prefers-reduced-motion: reduce)').matches
  );
}

function CountUp({ target, active }: { target: number; active: boolean }) {
  const [value, setValue] = useState(0);

  useEffect(() => {
    if (!active) return;
    if (prefersReducedMotion()) {
      setValue(target);
      return;
    }
    const duration = 900;
    let raf = 0;
    let start: number | null = null;
    const tick = (t: number) => {
      if (start === null) start = t;
      const p = Math.min((t - start) / duration, 1);
      const eased = 1 - Math.pow(1 - p, 3); // easeOutCubic
      setValue(Math.round(eased * target));
      if (p < 1) raf = requestAnimationFrame(tick);
    };
    raf = requestAnimationFrame(tick);
    return () => cancelAnimationFrame(raf);
  }, [active, target]);

  return <>{value}</>;
}

export default function SpecStrip() {
  const ref = useRef<HTMLDivElement>(null);
  const [active, setActive] = useState(false);

  useEffect(() => {
    const el = ref.current;
    if (!el) return;
    if (typeof IntersectionObserver === 'undefined') {
      setActive(true);
      return;
    }
    const io = new IntersectionObserver(
      (entries) => {
        if (entries[0]?.isIntersecting) {
          setActive(true);
          io.disconnect();
        }
      },
      { threshold: 0.4 }
    );
    io.observe(el);
    return () => io.disconnect();
  }, []);

  return (
    <section className="bg-canvas-elevated border-y border-hairline py-xl px-xs">
      <div
        ref={ref}
        className={`max-w-editorial mx-auto grid grid-cols-2 md:grid-cols-4 gap-px bg-hairline border border-hairline overflow-hidden ${
          active ? 'is-visible' : ''
        }`}
      >
        {stats.map(({ number, label }, i) => (
          <div
            key={label}
            className="reveal-cell bg-canvas-elevated px-md py-lg flex flex-col items-center text-center"
            style={{ transitionDelay: `${i * 80}ms` }}
          >
            <span
              className="text-ink block tabular-nums"
              style={{ fontSize: 'clamp(48px, 6vw, 80px)', fontWeight: 700, lineHeight: 1.0, letterSpacing: '-1.6px' }}
            >
              <CountUp target={number} active={active} />
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
