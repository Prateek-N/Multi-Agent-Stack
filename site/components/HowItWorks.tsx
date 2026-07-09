import { Reveal, Stagger } from './Reveal';
import Eyebrow from './ui/Eyebrow';

const phases = [
  {
    number: '0',
    name: 'Task Framing',
    key: 'task_framing',
    description: 'Orchestrator interprets your intent, detects domain automatically from the task text, and sets constraints.',
    artifact: 'task_profile',
  },
  {
    number: '1',
    name: 'Requirements',
    key: 'requirements',
    description: 'Architect Agent clarifies scope, surfaces ambiguities, and locks down what done looks like.',
    artifact: 'requirements_spec',
  },
  {
    number: '2',
    name: 'Solution Design',
    key: 'solution_design',
    description: 'Architect proposes the approach. UI and UX agents join automatically for product design tasks.',
    artifact: 'solution_design',
  },
  {
    number: '3',
    name: 'Implementation',
    key: 'implementation',
    description: 'Code Agent builds software; Execution Agent handles content, research, marketing, and ops.',
    artifact: 'work_product',
  },
  {
    number: '4',
    name: 'Review',
    key: 'review_refinement',
    description: 'Reviewer Agent critiques the output with severity-rated findings: CRITICAL / HIGH / MEDIUM / LOW.',
    artifact: 'refinement_report',
  },
  {
    number: '5',
    name: 'Handoff',
    key: 'handoff',
    description: 'Orchestrator packages all deliverables and surfaces next-project options. State persists for resumption.',
    artifact: 'handoff_package',
  },
];

export default function HowItWorks() {
  return (
    <section className="bg-canvas py-xxl px-xs">
      <div className="max-w-editorial mx-auto">
        <Reveal>
          <Eyebrow className="mb-sm">The Lifecycle</Eyebrow>

          <h2
            className="text-ink mb-xxl"
            style={{ fontSize: 'clamp(26px, 4vw, 56px)', fontWeight: 500, lineHeight: 1.1, letterSpacing: '-1.12px', maxWidth: '560px' }}
          >
            Six phases.
            <br />
            Every domain.
            <br />
            Every task.
          </h2>
        </Reveal>

        <Stagger className="space-y-0 border-l-2 border-hairline ml-sm md:ml-lg" step={90}>
          {phases.map((phase, i) => (
            <div
              key={phase.key}
              className="relative pl-lg pb-xl last:pb-0 group"
            >
              {/* Phase number bullet */}
              <div
                className="absolute -left-px top-0 w-px h-full"
                style={{ background: i === 0 ? '#da291c' : undefined }}
              />
              <div
                className="absolute -left-3 top-0 w-6 h-6 flex items-center justify-center text-primary bg-canvas border border-hairline group-hover:border-primary transition-colors"
                style={{ fontSize: '11px', fontWeight: 700, borderRadius: '0px' }}
              >
                {phase.number}
              </div>

              {/* Content */}
              <div className="ml-xs">
                <div className="flex items-center gap-sm mb-xxs flex-wrap">
                  <h3
                    className="text-ink"
                    style={{ fontSize: '18px', fontWeight: 700, lineHeight: 1.2 }}
                  >
                    {phase.name}
                  </h3>
                  {/* Artifact badge */}
                  <span
                    className="bg-canvas-elevated text-muted border border-hairline px-xs py-xxxs font-mono"
                    style={{ fontSize: '11px', borderRadius: '9999px' }}
                  >
                    → {phase.artifact}
                  </span>
                </div>
                <p className="text-body" style={{ fontSize: '14px', lineHeight: 1.6, maxWidth: '560px' }}>
                  {phase.description}
                </p>
              </div>
            </div>
          ))}
        </Stagger>

        <Reveal>
          <p
            className="text-muted mt-xxl border-t border-hairline pt-md"
            style={{ fontSize: '13px', lineHeight: 1.6 }}
          >
            Each phase ends with an approval gate — A/B/C options. The AI never proceeds without your sign-off.
            Small tasks can merge phases automatically.
          </p>
        </Reveal>
      </div>
    </section>
  );
}
