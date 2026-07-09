import type { ReactNode } from 'react';

/**
 * Eyebrow — the small uppercase section label used above every section heading.
 * Centralizes the previously inline-duplicated caption style so the design
 * token lives in one place. Renders identically to the prior inline markup.
 */
export default function Eyebrow({
  children,
  className = '',
  tone = 'primary',
}: {
  children: ReactNode;
  className?: string;
  tone?: 'primary' | 'muted';
}) {
  return (
    <p
      className={`${tone === 'primary' ? 'text-primary' : 'text-muted'} ${className}`.trim()}
      style={{ fontSize: '11px', fontWeight: 600, letterSpacing: '1.1px', textTransform: 'uppercase' }}
    >
      {children}
    </p>
  );
}
