import { REPO_URL } from '../lib/config';
import { Reveal } from './Reveal';

export default function CtaBand() {
  return (
    <section
      className="py-xxl px-xs"
      style={{ backgroundColor: '#da291c' }}
    >
      <Reveal className="max-w-editorial mx-auto flex flex-col md:flex-row items-start md:items-center justify-between gap-lg">
        <div>
          <h2
            className="text-white mb-sm"
            style={{ fontSize: 'clamp(26px, 4vw, 36px)', fontWeight: 500, lineHeight: 1.2, letterSpacing: '-0.36px' }}
          >
            Clone once. Use forever.
          </h2>
          <p className="text-white opacity-80" style={{ fontSize: '16px', lineHeight: 1.6, maxWidth: '480px' }}>
            Drop agents-maker into any project. Wire it into every AI platform
            in one command. Works with Claude, Copilot, Cursor, and Antigravity.
          </p>
        </div>

        <div className="flex flex-col sm:flex-row gap-sm flex-shrink-0">
          <a
            href={REPO_URL}
            target="_blank"
            rel="noopener noreferrer"
            className="inline-flex items-center justify-center border-2 border-white text-white hover:bg-white hover:text-primary transition-colors"
            style={{
              fontSize: '14px',
              fontWeight: 700,
              letterSpacing: '1.4px',
              textTransform: 'uppercase',
              padding: '13px 31px',
              height: '48px',
              borderRadius: '0px',
            }}
          >
            View on GitHub
          </a>
          <a
            href="#quickstart"
            className="inline-flex items-center justify-center bg-white text-primary hover:bg-opacity-90 transition-colors"
            style={{
              fontSize: '14px',
              fontWeight: 700,
              letterSpacing: '1.4px',
              textTransform: 'uppercase',
              padding: '14px 32px',
              height: '48px',
              borderRadius: '0px',
              color: '#da291c',
            }}
          >
            Get Started
          </a>
        </div>
      </Reveal>
    </section>
  );
}
