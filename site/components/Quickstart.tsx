import { NPM_PACKAGE } from '../lib/config';
import { Reveal } from './Reveal';
import Eyebrow from './ui/Eyebrow';

export default function Quickstart() {
  return (
    <section id="quickstart" className="scroll-mt-16 bg-canvas py-xxl px-xs border-t border-hairline">
      <div className="max-w-editorial mx-auto">
        <Reveal>
          <Eyebrow className="mb-sm">Quickstart</Eyebrow>

          <h2
            className="text-ink mb-xxl"
            style={{ fontSize: 'clamp(26px, 4vw, 56px)', fontWeight: 500, lineHeight: 1.1, letterSpacing: '-1.12px', maxWidth: '560px' }}
          >
            Up in 60 seconds.
          </h2>
        </Reveal>

        {/* CSS-only tab toggle */}
        <div className="relative">
          <input type="radio" name="qs-tab" id="tab-unix" className="sr-only" defaultChecked />
          <input type="radio" name="qs-tab" id="tab-win" className="sr-only" />

          {/* Tab labels */}
          <div className="tab-labels flex border-b border-hairline mb-md gap-lg">
            <label
              htmlFor="tab-unix"
              className="pb-sm cursor-pointer text-muted border-b-2 border-transparent transition-colors"
              style={{ fontSize: '13px', fontWeight: 600, letterSpacing: '0.65px', textTransform: 'uppercase' }}
            >
              macOS / Linux / WSL
            </label>
            <label
              htmlFor="tab-win"
              className="pb-sm cursor-pointer text-muted border-b-2 border-transparent transition-colors"
              style={{ fontSize: '13px', fontWeight: 600, letterSpacing: '0.65px', textTransform: 'uppercase' }}
            >
              Windows
            </label>
          </div>

          {/* Panels */}
          <div className="tab-panels">
            <div className="panel-unix">
              <CodeBlock lines={[
                { prompt: true, text: `npx ${NPM_PACKAGE} init` },
                { prompt: true, text: 'bash agents-maker/quickstart.sh' },
              ]} />
            </div>
            <div className="panel-win" style={{ display: 'none' }}>
              <CodeBlock lines={[
                { prompt: true, text: `npx ${NPM_PACKAGE} init`, ps: true },
                { prompt: true, text: '.\\agents-maker\\quickstart.ps1', ps: true },
              ]} />
            </div>
          </div>

          {/* Global install */}
          <div className="mt-xl">
            <p
              className="text-muted mb-sm"
              style={{ fontSize: '11px', fontWeight: 600, letterSpacing: '1.1px', textTransform: 'uppercase' }}
            >
              Or install globally — use across all your projects
            </p>
            <CodeBlock lines={[
              { prompt: true, text: `npm install -g ${NPM_PACKAGE}` },
              { prompt: true, text: 'agents-maker init' },
            ]} />
          </div>

          {/* What it does */}
          <div className="mt-lg border border-hairline bg-canvas-elevated overflow-hidden">
            <div
              className="px-md py-sm border-b border-hairline text-muted"
              style={{ fontSize: '11px', fontWeight: 600, letterSpacing: '1.1px', textTransform: 'uppercase' }}
            >
              What the script does
            </div>
            <div className="px-md py-sm space-y-xxs">
              {[
                'Checks Python 3.9+',
                'Installs pyyaml (the only dependency)',
                'Validates all 12 kit integrity checks',
                'Scans your project and generates system_prompt.md',
                'Prints all commands you need, ready to copy-paste',
              ].map((step, i) => (
                <div key={i} className="flex items-center gap-sm" style={{ fontSize: '14px' }}>
                  <span className="text-primary font-mono" style={{ minWidth: '20px' }}>{i + 1}.</span>
                  <span className="text-ink">{step}</span>
                </div>
              ))}
            </div>
          </div>

          {/* Daily use */}
          <div className="mt-xl">
            <p
              className="text-muted mb-sm"
              style={{ fontSize: '11px', fontWeight: 600, letterSpacing: '1.1px', textTransform: 'uppercase' }}
            >
              Then — before every AI session
            </p>
            <CodeBlock lines={[
              { prompt: true, text: 'python agents-maker/tools/generate_prompt.py "your task description"' },
              { prompt: false, text: '' },
              { prompt: false, text: '# Force a domain:' },
              { prompt: true, text: 'python agents-maker/tools/generate_prompt.py "[domain: software] refactor the auth module"' },
              { prompt: false, text: '' },
              { prompt: false, text: '# Add token compression:' },
              { prompt: true, text: 'python agents-maker/tools/generate_prompt.py "your task" --compress' },
            ]} />
          </div>
        </div>
      </div>
    </section>
  );
}

function CodeBlock({
  lines,
}: {
  lines: { prompt: boolean; text: string; ps?: boolean }[];
}) {
  return (
    <div
      className="bg-canvas border-l-2 border-primary overflow-x-auto"
      style={{ borderRadius: '0px' }}
    >
      <div className="px-md py-sm font-mono" style={{ fontSize: '13px', lineHeight: 1.7 }}>
        {lines.map((line, i) => (
          <div key={i} className={line.text === '' ? 'h-3' : ''}>
            {line.text !== '' && (
              <>
                {line.prompt && (
                  <span className="text-primary select-none mr-xxs">
                    {line.ps ? 'PS>' : '$'}
                  </span>
                )}
                {!line.prompt && (
                  <span className="text-muted">{line.text}</span>
                )}
                {line.prompt && (
                  <span className="text-ink">{line.text}</span>
                )}
              </>
            )}
          </div>
        ))}
      </div>
    </div>
  );
}
