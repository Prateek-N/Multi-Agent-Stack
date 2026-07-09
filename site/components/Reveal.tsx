'use client';

import {
  Children,
  cloneElement,
  isValidElement,
  useEffect,
  useRef,
  useState,
  type CSSProperties,
  type ReactElement,
  type ReactNode,
} from 'react';

function useInView<T extends HTMLElement>(rootMargin = '0px 0px -10% 0px', threshold = 0.15) {
  const ref = useRef<T>(null);
  const [inView, setInView] = useState(false);

  useEffect(() => {
    const el = ref.current;
    if (!el) return;
    // No IntersectionObserver (old browser / SSR safety) → reveal immediately.
    if (typeof IntersectionObserver === 'undefined') {
      setInView(true);
      return;
    }
    const io = new IntersectionObserver(
      (entries) => {
        if (entries[0]?.isIntersecting) {
          setInView(true);
          io.disconnect();
        }
      },
      { rootMargin, threshold }
    );
    io.observe(el);
    return () => io.disconnect();
  }, [rootMargin, threshold]);

  return { ref, inView };
}

/**
 * Reveal — fades + rises a single block into view when it scrolls near the viewport.
 * Use around headings, paragraphs, tables, code blocks — anything that reveals as one unit.
 */
export function Reveal({
  children,
  className = '',
  delay = 0,
  style,
}: {
  children: ReactNode;
  className?: string;
  delay?: number;
  style?: CSSProperties;
}) {
  const { ref, inView } = useInView<HTMLDivElement>();
  return (
    <div
      ref={ref}
      className={`reveal ${inView ? 'is-visible' : ''} ${className}`}
      style={{ transitionDelay: `${delay}ms`, ...style }}
    >
      {children}
    </div>
  );
}

/**
 * Stagger — reveals the direct children of a grid/list one after another.
 * Preserves the original container element and its direct children exactly
 * (grid layout is untouched); it only tags each child with a class + staggered
 * transition-delay, so it is safe to wrap existing `gap-px` grids.
 */
export function Stagger({
  children,
  className = '',
  step = 70,
  base = 0,
  style,
}: {
  children: ReactNode;
  className?: string;
  step?: number;
  base?: number;
  style?: CSSProperties;
}) {
  const { ref, inView } = useInView<HTMLDivElement>();
  return (
    <div ref={ref} className={`${inView ? 'is-visible' : ''} ${className}`} style={style}>
      {Children.map(children, (child, i) => {
        if (!isValidElement(child)) return child;
        const el = child as ReactElement<{ className?: string; style?: CSSProperties }>;
        return cloneElement(el, {
          className: `${el.props.className ?? ''} reveal-cell`.trim(),
          style: { ...el.props.style, transitionDelay: `${base + i * step}ms` },
        });
      })}
    </div>
  );
}
