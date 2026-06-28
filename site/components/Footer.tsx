const REPO = 'https://github.com/Prateek-N/Multi-Agent-Stack';

const cols = [
  {
    title: 'Product',
    links: [
      { label: 'Quickstart', href: '#quickstart' },
      { label: 'Agents', href: '#agents' },
      { label: 'Skills', href: '#skills' },
      { label: 'Platforms', href: '#platforms' },
      { label: 'Changelog', href: `${REPO}/blob/main/CHANGELOG.md` },
    ],
  },
  {
    title: 'Platforms',
    links: [
      { label: 'Claude Code', href: `${REPO}/blob/main/platforms/claude.md` },
      { label: 'GitHub Copilot', href: `${REPO}#platform-integration` },
      { label: 'Cursor', href: `${REPO}#platform-integration` },
      { label: 'Antigravity', href: `${REPO}/blob/main/platforms/antigravity.md` },
      { label: 'OpenAI', href: `${REPO}/blob/main/platforms/openai.md` },
    ],
  },
  {
    title: 'Docs',
    links: [
      { label: 'Architecture', href: `${REPO}/blob/main/docs/architecture.md` },
      { label: 'Workflows', href: `${REPO}/blob/main/docs/workflows.md` },
      { label: 'Domains', href: `${REPO}/blob/main/docs/domains.md` },
      { label: 'Examples', href: `${REPO}/blob/main/examples/generic_project_lifecycle.md` },
      { label: 'Contributing', href: `${REPO}/blob/main/CONTRIBUTING.md` },
    ],
  },
  {
    title: 'Connect',
    links: [
      { label: 'GitHub', href: REPO },
      { label: 'Issues', href: `${REPO}/issues` },
      { label: 'Releases', href: `${REPO}/releases` },
      { label: 'MIT License', href: `${REPO}/blob/main/LICENSE` },
    ],
  },
];

export default function Footer() {
  return (
    <footer className="bg-canvas border-t border-hairline pt-xxl pb-xl px-xs">
      <div className="max-w-editorial mx-auto">
        {/* Logo row */}
        <div className="flex items-center gap-xxs mb-xxl">
          <span className="w-2 h-2 rounded-full bg-primary flex-shrink-0" />
          <span
            className="text-ink font-semibold"
            style={{ fontSize: '15px', letterSpacing: '-0.2px' }}
          >
            agents-maker
          </span>
        </div>

        {/* Link columns */}
        <div className="grid grid-cols-2 md:grid-cols-4 gap-lg mb-xxl">
          {cols.map((col) => (
            <div key={col.title}>
              <p
                className="text-ink mb-sm"
                style={{ fontSize: '11px', fontWeight: 600, letterSpacing: '1.1px', textTransform: 'uppercase' }}
              >
                {col.title}
              </p>
              <ul className="space-y-xxs">
                {col.links.map((link) => (
                  <li key={link.label}>
                    <a
                      href={link.href}
                      target={link.href.startsWith('http') ? '_blank' : undefined}
                      rel={link.href.startsWith('http') ? 'noopener noreferrer' : undefined}
                      className="text-body hover:text-ink transition-colors"
                      style={{ fontSize: '13px', lineHeight: 1.5 }}
                    >
                      {link.label}
                    </a>
                  </li>
                ))}
              </ul>
            </div>
          ))}
        </div>

        {/* Bottom strip */}
        <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-xs border-t border-hairline pt-md">
          <p className="text-muted" style={{ fontSize: '13px' }}>
            MIT License · Built by{' '}
            <a
              href="https://github.com/Prateek-N"
              target="_blank"
              rel="noopener noreferrer"
              className="text-body hover:text-ink transition-colors"
            >
              Prateek Narvariya
            </a>
          </p>
          <p className="text-muted" style={{ fontSize: '13px' }}>
            agents-maker v1.0 · Pure Markdown + YAML · No API keys
          </p>
        </div>
      </div>
    </footer>
  );
}
