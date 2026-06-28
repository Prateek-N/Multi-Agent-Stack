export default function Nav() {
  return (
    <header className="fixed top-0 left-0 right-0 z-50 bg-canvas border-b border-hairline h-16 flex items-center">
      <div className="w-full max-w-editorial mx-auto px-xs flex items-center justify-between">
        {/* Wordmark */}
        <a href="/" className="flex items-center gap-xxs group">
          <span className="w-2 h-2 rounded-full bg-primary flex-shrink-0" />
          <span
            className="text-ink font-semibold tracking-tight"
            style={{ fontSize: '15px', letterSpacing: '-0.2px' }}
          >
            agents-maker
          </span>
        </a>

        {/* Nav links */}
        <nav className="hidden md:flex items-center gap-lg">
          {[
            { label: 'GITHUB', href: 'https://github.com/Prateek-N/Multi-Agent-Stack' },
            { label: 'DOCS', href: 'https://github.com/Prateek-N/Multi-Agent-Stack#readme' },
            { label: 'QUICKSTART', href: '#quickstart' },
          ].map(({ label, href }) => (
            <a
              key={label}
              href={href}
              target={href.startsWith('http') ? '_blank' : undefined}
              rel={href.startsWith('http') ? 'noopener noreferrer' : undefined}
              className="text-body hover:text-ink transition-colors duration-150"
              style={{
                fontSize: '13px',
                fontWeight: 600,
                letterSpacing: '0.65px',
                textTransform: 'uppercase',
              }}
            >
              {label}
            </a>
          ))}
        </nav>

        {/* Mobile — GitHub icon only */}
        <a
          href="https://github.com/Prateek-N/Multi-Agent-Stack"
          target="_blank"
          rel="noopener noreferrer"
          className="md:hidden text-body hover:text-ink transition-colors"
          aria-label="GitHub"
        >
          <svg width="20" height="20" viewBox="0 0 24 24" fill="currentColor">
            <path d="M12 0C5.37 0 0 5.37 0 12c0 5.31 3.435 9.795 8.205 11.385.6.105.825-.255.825-.57 0-.285-.015-1.23-.015-2.235-3.015.555-3.795-.735-4.035-1.41-.135-.345-.72-1.41-1.23-1.695-.42-.225-1.02-.78-.015-.795.945-.015 1.62.87 1.845 1.23 1.08 1.815 2.805 1.305 3.495.99.105-.78.42-1.305.765-1.605-2.67-.3-5.46-1.335-5.46-5.925 0-1.305.465-2.385 1.23-3.225-.12-.3-.54-1.53.12-3.18 0 0 1.005-.315 3.3 1.23.96-.27 1.98-.405 3-.405s2.04.135 3 .405c2.295-1.56 3.3-1.23 3.3-1.23.66 1.65.24 2.88.12 3.18.765.84 1.23 1.905 1.23 3.225 0 4.605-2.805 5.625-5.475 5.925.435.375.81 1.095.81 2.22 0 1.605-.015 2.895-.015 3.3 0 .315.225.69.825.57A12.02 12.02 0 0 0 24 12c0-6.63-5.37-12-12-12Z" />
          </svg>
        </a>
      </div>
    </header>
  );
}
