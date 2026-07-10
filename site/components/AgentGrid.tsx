import { Reveal, Stagger } from './Reveal';
import Eyebrow from './ui/Eyebrow';

const agents = [
  {
    id: 'brain',
    name: 'Brain',
    role: 'Brainstorming',
    command: '/brain',
    description: 'Brainstorm the whole project — 3+ genuinely different approaches with trade-offs, then one recommendation.',
    alwaysActive: false,
  },
  {
    id: 'planpro',
    name: 'PlanPro',
    role: 'Planning',
    command: '/planpro',
    description: 'Turn a goal into the best-possible plan: short, specific, dependency-ordered, and verifiable.',
    alwaysActive: false,
  },
  {
    id: 'orchestrator',
    name: 'Orchestrator',
    role: 'Supervisor',
    command: '/orchestrate',
    description: 'Entry point for every task. Detects domain, drives the 6-phase lifecycle, aggregates output. Always active.',
    alwaysActive: true,
  },
  {
    id: 'architect_agent',
    name: 'Architect',
    role: 'System Design',
    command: '/architect',
    description: 'System design, API contracts, research plans, campaign strategy, and process maps.',
    alwaysActive: false,
  },
  {
    id: 'code_agent',
    name: 'Code Agent',
    role: 'Implementation',
    command: '/code',
    description: 'Software implementation, refactoring, and test generation for software and data analytics domains.',
    alwaysActive: false,
  },
  {
    id: 'execution_agent',
    name: 'Execution Agent',
    role: 'Non-Code Work',
    command: '/execute',
    description: 'Documents, research sections, marketing copy, SOPs, and runbooks. Everything not code.',
    alwaysActive: false,
  },
  {
    id: 'ui_agent',
    name: 'UI Agent',
    role: 'Presentation Layer',
    command: '/ui',
    description: 'Component hierarchy, layout, design tokens, accessibility, and landing page architecture.',
    alwaysActive: false,
  },
  {
    id: 'ux_agent',
    name: 'UX Agent',
    role: 'Experience Design',
    command: '/ux',
    description: 'Flow critique, onboarding sequences, funnel analysis, and friction identification.',
    alwaysActive: false,
  },
  {
    id: 'reviewer_agent',
    name: 'Reviewer Agent',
    role: 'Quality Assurance',
    command: '/review',
    description: 'Severity-rated QA review for any domain: CRITICAL / HIGH / MEDIUM / LOW.',
    alwaysActive: false,
  },
  {
    id: 'compression_agent',
    name: 'Compression Agent',
    role: 'Context Management',
    command: '/compress',
    description: 'Token budget enforcement, context compression, and cross-session resumption without history replay.',
    alwaysActive: false,
  },
];

export default function AgentGrid() {
  return (
    <section id="agents" className="scroll-mt-16 bg-canvas py-xxl px-xs border-t border-hairline">
      <div className="max-w-editorial mx-auto">
        <Reveal>
          <Eyebrow className="mb-sm">10 Named Agents</Eyebrow>

          <h2
            className="text-ink mb-xxl"
            style={{ fontSize: 'clamp(26px, 4vw, 56px)', fontWeight: 500, lineHeight: 1.1, letterSpacing: '-1.12px', maxWidth: '560px' }}
          >
            The right expert,
            <br />
            on command.
          </h2>
        </Reveal>

        <Stagger className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-px bg-hairline border border-hairline overflow-hidden" step={60}>
          {agents.map((agent) => (
            <div
              key={agent.id}
              className={`bg-canvas-elevated p-md flex flex-col group hover:bg-canvas transition-colors ${
                agent.alwaysActive ? 'border-t-2 border-t-primary' : ''
              }`}
            >
              <div className="flex items-start justify-between mb-sm gap-xxs">
                <h3
                  className="text-ink"
                  style={{ fontSize: '18px', fontWeight: 700, lineHeight: 1.2 }}
                >
                  {agent.name}
                </h3>
                <span className="flex-shrink-0 flex items-center gap-xxs" style={{ marginTop: '2px' }}>
                  <span
                    className="font-mono text-primary"
                    style={{ fontSize: '12px', fontWeight: 500 }}
                  >
                    {agent.command}
                  </span>
                  {agent.alwaysActive && (
                    <span
                      className="bg-primary text-white"
                      style={{
                        fontSize: '9px',
                        fontWeight: 600,
                        letterSpacing: '0.8px',
                        textTransform: 'uppercase',
                        padding: '2px 6px',
                        borderRadius: '0px',
                      }}
                    >
                      Always on
                    </span>
                  )}
                </span>
              </div>
              <span
                className="text-muted mb-sm block"
                style={{ fontSize: '11px', fontWeight: 600, letterSpacing: '1.1px', textTransform: 'uppercase' }}
              >
                {agent.role}
              </span>
              <p className="text-body flex-1" style={{ fontSize: '13px', lineHeight: 1.6 }}>
                {agent.description}
              </p>
            </div>
          ))}
        </Stagger>

        <Reveal>
          <p className="text-muted mt-md" style={{ fontSize: '13px', lineHeight: 1.6 }}>
            Invoke any agent by name (<code className="font-mono text-ink" style={{ fontSize: '12px' }}>/brain</code>,
            {' '}<code className="font-mono text-ink" style={{ fontSize: '12px' }}>/planpro</code>, …) after
            {' '}<code className="font-mono text-ink" style={{ fontSize: '12px' }}>npx @prateek_ai/agents-maker init</code> installs
            them into your <code className="font-mono text-ink" style={{ fontSize: '12px' }}>.claude/</code> — or let the
            Orchestrator route automatically. All agent specs are plain Markdown, portable to any AI tool.
          </p>
        </Reveal>
      </div>
    </section>
  );
}
