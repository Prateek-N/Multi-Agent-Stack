import { Reveal, Stagger } from './Reveal';
import Eyebrow from './ui/Eyebrow';

const agents = [
  {
    id: 'orchestrator',
    name: 'Orchestrator',
    role: 'Supervisor',
    description: 'Entry point for every task. Detects domain, drives the 6-phase lifecycle, aggregates output. Always active.',
    alwaysActive: true,
  },
  {
    id: 'architect_agent',
    name: 'Architect',
    role: 'System Design',
    description: 'System design, API contracts, research plans, campaign strategy, and process maps.',
    alwaysActive: false,
  },
  {
    id: 'code_agent',
    name: 'Code Agent',
    role: 'Implementation',
    description: 'Software implementation, refactoring, and test generation for software and data analytics domains.',
    alwaysActive: false,
  },
  {
    id: 'execution_agent',
    name: 'Execution Agent',
    role: 'Non-Code Work',
    description: 'Documents, research sections, marketing copy, SOPs, and runbooks. Everything not code.',
    alwaysActive: false,
  },
  {
    id: 'ui_agent',
    name: 'UI Agent',
    role: 'Presentation Layer',
    description: 'Component hierarchy, layout, design tokens, accessibility, and landing page architecture.',
    alwaysActive: false,
  },
  {
    id: 'ux_agent',
    name: 'UX Agent',
    role: 'Experience Design',
    description: 'Flow critique, onboarding sequences, funnel analysis, and friction identification.',
    alwaysActive: false,
  },
  {
    id: 'reviewer_agent',
    name: 'Reviewer Agent',
    role: 'Quality Assurance',
    description: 'Severity-rated QA review for any domain: CRITICAL / HIGH / MEDIUM / LOW.',
    alwaysActive: false,
  },
  {
    id: 'compression_agent',
    name: 'Compression Agent',
    role: 'Context Management',
    description: 'Token budget enforcement, context compression, and cross-session resumption without history replay.',
    alwaysActive: false,
  },
];

export default function AgentGrid() {
  return (
    <section id="agents" className="scroll-mt-16 bg-canvas py-xxl px-xs border-t border-hairline">
      <div className="max-w-editorial mx-auto">
        <Reveal>
          <Eyebrow className="mb-sm">8 Specialist Agents</Eyebrow>

          <h2
            className="text-ink mb-xxl"
            style={{ fontSize: 'clamp(26px, 4vw, 56px)', fontWeight: 500, lineHeight: 1.1, letterSpacing: '-1.12px', maxWidth: '560px' }}
          >
            The right expert,
            <br />
            automatically.
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
                {agent.alwaysActive && (
                  <span
                    className="flex-shrink-0 bg-primary text-white px-xxs"
                    style={{
                      fontSize: '9px',
                      fontWeight: 600,
                      letterSpacing: '0.8px',
                      textTransform: 'uppercase',
                      padding: '2px 6px',
                      borderRadius: '0px',
                      marginTop: '2px',
                    }}
                  >
                    Always on
                  </span>
                )}
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
            You never name an agent. The Orchestrator selects specialists automatically based on
            domain and phase. All agent specs are plain Markdown — paste any one directly into
            any AI tool.
          </p>
        </Reveal>
      </div>
    </section>
  );
}
