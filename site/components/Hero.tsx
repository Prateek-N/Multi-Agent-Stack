import { REPO_URL } from '../lib/config';

const TERMINAL_LINES = [
  { text: '$ python agents-maker/tools/generate_prompt.py "add rate limiting to auth service"', cls: 'text-body-strong' },
  { text: '', cls: '' },
  { text: '━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━', cls: 'text-hairline' },
  { text: '  PASTE THIS AS YOUR NEXT MESSAGE', cls: 'text-primary font-semibold' },
  { text: '  Project: my-app  |  Domain: software (high)  |  Phase: implementation', cls: 'text-muted' },
  { text: '  Est. tokens: ~3,800  |  Agents: orchestrator, code_agent', cls: 'text-muted' },
  { text: '━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━', cls: 'text-hairline' },
  { text: '', cls: '' },
  { text: '## Project Context', cls: 'text-primary' },
  { text: 'Name: my-app  |  Stack: python, fastapi, postgres  |  Domain: software', cls: 'text-ink' },
  { text: '', cls: '' },
  { text: '## Domain & Routing', cls: 'text-primary' },
  { text: 'Domain: software (confidence: high, score: 1.33)', cls: 'text-ink' },
  { text: 'Active agents: orchestrator, code_agent', cls: 'text-ink' },
  { text: 'Active skills: review_code, write_tests, suggest_next', cls: 'text-muted-soft' },
];

export default function Hero() {
  return (
    <section className="relative bg-canvas min-h-screen flex flex-col overflow-hidden pt-16">
      {/* Grid overlay — subtle depth */}
      <div
        className="absolute inset-0 pointer-events-none"
        style={{
          backgroundImage:
            'linear-gradient(rgba(48,48,48,0.15) 1px, transparent 1px), linear-gradient(90deg, rgba(48,48,48,0.15) 1px, transparent 1px)',
          backgroundSize: '64px 64px',
        }}
      />

      {/* Terminal window — top half */}
      <div className="flex-1 flex items-start justify-center px-xs pt-xxl pb-md">
        <div className="w-full max-w-3xl">
          {/* Window chrome */}
          <div className="bg-canvas-elevated border border-hairline rounded-none">
            <div className="flex items-center gap-xxs px-sm py-xxs border-b border-hairline">
              <span className="w-3 h-3 rounded-full bg-primary opacity-80" />
              <span className="w-3 h-3 rounded-full bg-body opacity-40" />
              <span className="w-3 h-3 rounded-full bg-body opacity-40" />
              <span className="ml-auto text-muted" style={{ fontSize: '11px', letterSpacing: '0.5px' }}>
                terminal
              </span>
            </div>
            {/* Terminal body */}
            <div className="px-sm py-sm font-mono" style={{ fontSize: '12px', lineHeight: '1.7' }}>
              {TERMINAL_LINES.map((line, i) => (
                <div key={i} className={`terminal-line ${line.cls}`}>
                  {line.text || ' '}
                </div>
              ))}
              {/* Cursor */}
              <div className="terminal-line text-primary" style={{ animationDelay: '3.1s' }}>
                <span
                  className="inline-block w-2 h-4 bg-primary"
                  style={{ animation: 'blink 1s step-end infinite', verticalAlign: 'text-bottom' }}
                />
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Headline block — bottom */}
      <div className="relative px-xs pb-xxl pt-lg border-t border-hairline">
        {/* Red gradient line at top */}
        <div
          className="absolute top-0 left-0 right-0 h-px"
          style={{ background: 'linear-gradient(90deg, transparent, #da291c 30%, #da291c 70%, transparent)' }}
        />

        <div className="max-w-editorial mx-auto">
          <p
            className="hero-headline text-ink mb-sm"
            style={{
              fontSize: 'clamp(32px, 6vw, 80px)',
              fontWeight: 500,
              lineHeight: 1.05,
              letterSpacing: '-1.6px',
            }}
          >
            Multi-Agent AI.
            <br />
            Any Project.{' '}
            <span className="text-primary">Any Tool.</span>
          </p>

          <p
            className="hero-sub text-body mb-lg"
            style={{ fontSize: 'clamp(14px, 1.5vw, 18px)', maxWidth: '560px', lineHeight: 1.6 }}
          >
            Drop it in. Detect domain. Route to the right specialist.
            <br className="hidden md:block" /> Always know what to do next.
          </p>

          <div className="hero-ctas flex flex-wrap gap-sm">
            <a
              href="#quickstart"
              className="inline-flex items-center justify-center bg-primary hover:bg-primary-active text-white transition-colors"
              style={{
                fontSize: '14px',
                fontWeight: 700,
                letterSpacing: '1.4px',
                textTransform: 'uppercase',
                padding: '14px 32px',
                height: '48px',
                borderRadius: '0px',
              }}
            >
              Get Started
            </a>
            <a
              href={REPO_URL}
              target="_blank"
              rel="noopener noreferrer"
              className="inline-flex items-center justify-center border border-ink text-ink hover:bg-canvas-elevated transition-colors"
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
          </div>
        </div>
      </div>

      <style>{`
        @keyframes blink { 0%,100%{opacity:1} 50%{opacity:0} }
      `}</style>
    </section>
  );
}
