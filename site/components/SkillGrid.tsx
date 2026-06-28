const skills = [
  { key: 'analyze_repo',       label: 'Analyze Repo',       desc: 'Stack detection, entrypoints, service map' },
  { key: 'design_api',         label: 'Design API',         desc: 'REST, GraphQL, and RPC contract drafts' },
  { key: 'review_code',        label: 'Review Code',        desc: 'Severity-rated correctness, security, perf' },
  { key: 'review_layout',      label: 'Review Layout',      desc: 'Visual hierarchy, spacing, a11y critique' },
  { key: 'improve_copy',       label: 'Improve Copy',       desc: 'Microcopy, CTAs, errors, empty states' },
  { key: 'write_tests',        label: 'Write Tests',        desc: 'Unit and integration test stubs' },
  { key: 'summarize_history',  label: 'Summarize History',  desc: 'Cross-session compression and handoff' },
  { key: 'suggest_next',       label: 'Suggest Next',       desc: 'Auto-fires — 3 ranked next moves always' },
  { key: 'compare_approaches', label: 'Compare Approaches', desc: 'Structured trade-off table, one recommendation' },
  { key: 'animated_website',   label: 'Animated Website',   desc: 'CSS/GSAP/Framer Motion production code' },
  { key: 'write_process_map',  label: 'Write Process Map',  desc: 'Steps + RACI matrix + exception table' },
  { key: 'define_data_schema', label: 'Define Data Schema', desc: 'ER sketch + metrics + data dictionary' },
];

export default function SkillGrid() {
  return (
    <section className="bg-canvas-elevated py-xxl px-xs border-y border-hairline">
      <div className="max-w-editorial mx-auto">
        <p
          className="text-primary mb-sm"
          style={{ fontSize: '11px', fontWeight: 600, letterSpacing: '1.1px', textTransform: 'uppercase' }}
        >
          12 Reusable Skills
        </p>

        <h2
          className="text-ink mb-xxl"
          style={{ fontSize: 'clamp(26px, 4vw, 36px)', fontWeight: 500, lineHeight: 1.2, letterSpacing: '-0.36px', maxWidth: '480px' }}
        >
          Plug-in capabilities that activate when you need them.
        </h2>

        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-px bg-hairline border border-hairline overflow-hidden">
          {skills.map((skill) => (
            <div
              key={skill.key}
              className="bg-canvas-elevated px-md py-sm group hover:bg-canvas transition-colors flex flex-col gap-xxs"
            >
              <span
                className="text-ink"
                style={{ fontSize: '14px', fontWeight: 700, letterSpacing: '0.2px' }}
              >
                {skill.label}
              </span>
              <span className="text-body" style={{ fontSize: '13px', lineHeight: 1.5 }}>
                {skill.desc}
              </span>
              <span
                className="text-muted font-mono"
                style={{ fontSize: '11px', marginTop: '2px' }}
              >
                {skill.key}.md
              </span>
            </div>
          ))}
        </div>

        <p className="text-muted mt-md" style={{ fontSize: '13px', lineHeight: 1.6 }}>
          Skills are plain Markdown files. Add your own by dropping a new .md into{' '}
          <code className="font-mono text-ink bg-canvas px-xxs" style={{ fontSize: '12px' }}>
            agents-maker/skills/
          </code>
          .
        </p>
      </div>
    </section>
  );
}
