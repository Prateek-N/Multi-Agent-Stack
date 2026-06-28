const platforms = [
  {
    name: 'Claude Code',
    file: 'CLAUDE.md',
    description: 'Auto-loaded every session via Project Instructions. Domain, phase, and agent routing — zero copy-paste.',
    color: '#8B5CF6',
    icon: (
      <svg viewBox="0 0 24 24" fill="currentColor" className="w-5 h-5">
        <path d="M12 2L2 7l10 5 10-5-10-5zM2 17l10 5 10-5M2 12l10 5 10-5" stroke="currentColor" strokeWidth="2" fill="none" />
      </svg>
    ),
  },
  {
    name: 'GitHub Copilot',
    file: '.github/copilot-instructions.md',
    description: 'Workspace-level instructions. Copilot applies agent routing automatically on every suggestion.',
    color: '#2EA44F',
    icon: (
      <svg viewBox="0 0 24 24" fill="currentColor" className="w-5 h-5">
        <path d="M12 0C5.37 0 0 5.37 0 12c0 5.31 3.435 9.795 8.205 11.385.6.105.825-.255.825-.57 0-.285-.015-1.23-.015-2.235-3.015.555-3.795-.735-4.035-1.41-.135-.345-.72-1.41-1.23-1.695-.42-.225-1.02-.78-.015-.795.945-.015 1.62.87 1.845 1.23 1.08 1.815 2.805 1.305 3.495.99.105-.78.42-1.305.765-1.605-2.67-.3-5.46-1.335-5.46-5.925 0-1.305.465-2.385 1.23-3.225-.12-.3-.54-1.53.12-3.18 0 0 1.005-.315 3.3 1.23.96-.27 1.98-.405 3-.405s2.04.135 3 .405c2.295-1.56 3.3-1.23 3.3-1.23.66 1.65.24 2.88.12 3.18.765.84 1.23 1.905 1.23 3.225 0 4.605-2.805 5.625-5.475 5.925.435.375.81 1.095.81 2.22 0 1.605-.015 2.895-.015 3.3 0 .315.225.69.825.57A12.02 12.02 0 0 0 24 12c0-6.63-5.37-12-12-12Z" />
      </svg>
    ),
  },
  {
    name: 'Cursor',
    file: '.cursor/rules',
    description: 'Persistent AI rules across all tabs. Domain context and phase tracking applied on every interaction.',
    color: '#00A9FF',
    icon: (
      <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" className="w-5 h-5">
        <rect x="3" y="3" width="18" height="18" rx="2" />
        <path d="M9 12h6M12 9v6" />
      </svg>
    ),
  },
  {
    name: 'Antigravity',
    file: '.agkit/agents.yaml',
    description: 'Full agent pipeline config — all 8 agents and 12 skills registered with phase and domain wiring.',
    color: '#F59E0B',
    icon: (
      <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" className="w-5 h-5">
        <circle cx="12" cy="12" r="3" />
        <path d="M12 1v4M12 19v4M4.22 4.22l2.83 2.83M16.95 16.95l2.83 2.83M1 12h4M19 12h4M4.22 19.78l2.83-2.83M16.95 7.05l2.83-2.83" />
      </svg>
    ),
  },
];

export default function Platforms() {
  return (
    <section className="bg-canvas py-xxl px-xs border-t border-hairline">
      <div className="max-w-editorial mx-auto">
        <p
          className="text-primary mb-sm"
          style={{ fontSize: '11px', fontWeight: 600, letterSpacing: '1.1px', textTransform: 'uppercase' }}
        >
          Works Everywhere
        </p>

        <h2
          className="text-ink mb-md"
          style={{ fontSize: 'clamp(26px, 4vw, 56px)', fontWeight: 500, lineHeight: 1.1, letterSpacing: '-1.12px', maxWidth: '640px' }}
        >
          Wire into every AI platform
          <br />
          with one command.
        </h2>

        <p className="text-body mb-xxl" style={{ fontSize: '14px', lineHeight: 1.7, maxWidth: '520px' }}>
          agents-maker writes a native config file for each platform — committed to git,
          auto-loaded on every session. No copy-paste required.
        </p>

        {/* Platform cards */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-px bg-hairline border border-hairline mb-xxl overflow-hidden">
          {platforms.map((p) => (
            <div
              key={p.name}
              className="bg-canvas-elevated p-md group hover:bg-canvas transition-colors"
            >
              <div className="flex items-start gap-sm">
                <div
                  className="flex-shrink-0 p-xxs border border-hairline group-hover:border-current transition-colors"
                  style={{ color: p.color, borderRadius: '0px' }}
                >
                  {p.icon}
                </div>
                <div className="min-w-0">
                  <h3
                    className="text-ink mb-xxs"
                    style={{ fontSize: '18px', fontWeight: 700, lineHeight: 1.2 }}
                  >
                    {p.name}
                  </h3>
                  <p
                    className="font-mono text-muted mb-xs"
                    style={{ fontSize: '11px', letterSpacing: '0.3px' }}
                  >
                    {p.file}
                  </p>
                  <p className="text-body" style={{ fontSize: '13px', lineHeight: 1.6 }}>
                    {p.description}
                  </p>
                </div>
              </div>
            </div>
          ))}
        </div>

        {/* Single command */}
        <div>
          <p
            className="text-muted mb-sm"
            style={{ fontSize: '11px', fontWeight: 600, letterSpacing: '1.1px', textTransform: 'uppercase' }}
          >
            One Command, All Platforms
          </p>
          <div
            className="bg-canvas-elevated border border-hairline px-md py-sm font-mono overflow-x-auto"
            style={{ borderRadius: '0px' }}
          >
            <span className="text-primary select-none">$ </span>
            <span className="text-ink">python agents-maker/tools/generate_platform_configs.py</span>
          </div>
          <p className="text-muted mt-xxs" style={{ fontSize: '12px' }}>
            Commit the generated files — they are project config, not private state.
          </p>
        </div>
      </div>
    </section>
  );
}
