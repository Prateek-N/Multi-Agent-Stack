import { Reveal } from './Reveal';
import Eyebrow from './ui/Eyebrow';

const rows = [
  { without: 'Re-explain the project every session', with: 'project_state.md resumes automatically' },
  { without: 'AI gives generic boilerplate patterns', with: 'Specialist agent uses your actual stack' },
  { without: 'Wrong domain, wrong agent, wrong output', with: 'Domain auto-detected from task description' },
  { without: 'Bloated context, slow token-heavy responses', with: 'Token budget enforced per phase and domain' },
  { without: '"What do I do next?" after every response', with: '3 ranked next steps surfaced automatically' },
  { without: 'One-size-fits-all output style', with: '11 output styles matched to phase and task' },
];

export default function ProblemSolution() {
  return (
    <section className="bg-canvas py-xxl px-xs">
      <div className="max-w-editorial mx-auto">
        <Reveal>
          {/* Label */}
          <Eyebrow className="mb-sm">The Problem</Eyebrow>

          {/* Headline */}
          <h2
            className="text-ink mb-xxl"
            style={{ fontSize: 'clamp(26px, 4vw, 56px)', fontWeight: 500, lineHeight: 1.1, letterSpacing: '-1.12px', maxWidth: '640px' }}
          >
            AI quality is bounded
            <br />
            by context quality.
          </h2>
        </Reveal>

        {/* Table */}
        <Reveal delay={80} className="border border-hairline overflow-hidden">
          {/* Header */}
          <div className="grid grid-cols-2 border-b border-hairline">
            <div
              className="px-md py-sm text-muted border-r border-hairline"
              style={{ fontSize: '11px', fontWeight: 600, letterSpacing: '1.1px', textTransform: 'uppercase' }}
            >
              Without agents-maker
            </div>
            <div
              className="px-md py-sm flex items-center gap-xs"
              style={{ fontSize: '11px', fontWeight: 600, letterSpacing: '1.1px', textTransform: 'uppercase' }}
            >
              <span className="w-1.5 h-1.5 rounded-full bg-primary flex-shrink-0" />
              <span className="text-ink">With agents-maker</span>
            </div>
          </div>

          {/* Rows */}
          {rows.map((row, i) => (
            <div
              key={i}
              className="grid grid-cols-2 border-b border-hairline last:border-b-0 hover:bg-canvas-elevated transition-colors"
            >
              <div className="px-md py-sm text-muted text-body-md border-r border-hairline" style={{ fontSize: '14px' }}>
                {row.without}
              </div>
              <div className="px-md py-sm flex items-start gap-xs">
                <svg
                  className="w-4 h-4 text-primary flex-shrink-0 mt-0.5"
                  viewBox="0 0 16 16"
                  fill="none"
                  stroke="currentColor"
                  strokeWidth="2"
                >
                  <polyline points="2 8 6 12 14 4" />
                </svg>
                <span className="text-ink" style={{ fontSize: '14px' }}>{row.with}</span>
              </div>
            </div>
          ))}
        </Reveal>
      </div>
    </section>
  );
}
