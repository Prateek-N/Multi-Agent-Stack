import type { Metadata } from 'next';
import './globals.css';
import { SITE_URL } from '../lib/config';

export const metadata: Metadata = {
  metadataBase: new URL(SITE_URL),
  title: 'agents-maker — Multi-Agent AI for Any Project, Any Tool',
  description:
    'Drop it into your project. Auto-detect domain. Route to the right specialist agent. Always know what to do next. Works with Claude, Copilot, Cursor, and Antigravity.',
  openGraph: {
    title: 'agents-maker',
    description: 'Multi-Agent AI. Any Project. Any Tool.',
    images: ['/og.png'],
    type: 'website',
  },
  twitter: {
    card: 'summary_large_image',
    title: 'agents-maker — Multi-Agent AI for Any Project, Any Tool',
    description: 'Drop it in. Detect domain. Route to the right specialist. Always know what\'s next.',
    images: ['/og.png'],
  },
  keywords: [
    'multi-agent AI', 'Claude Code', 'GitHub Copilot', 'Cursor', 'Antigravity',
    'AI agents', 'prompt engineering', 'LLM framework', 'developer tools',
  ],
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en" className="bg-canvas no-js" suppressHydrationWarning>
      <head>
        {/* Strip .no-js before paint so scroll-reveal is armed; content stays visible if JS is off. */}
        <script
          dangerouslySetInnerHTML={{
            __html: "document.documentElement.classList.remove('no-js')",
          }}
        />
        <link rel="preconnect" href="https://fonts.googleapis.com" />
        <link rel="preconnect" href="https://fonts.gstatic.com" crossOrigin="anonymous" />
        <link
          href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=JetBrains+Mono:wght@400;500&display=swap"
          rel="stylesheet"
        />
      </head>
      <body className="bg-canvas text-ink antialiased">{children}</body>
    </html>
  );
}
