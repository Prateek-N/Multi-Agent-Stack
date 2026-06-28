import type { Config } from 'tailwindcss';

const config: Config = {
  content: [
    './app/**/*.{js,ts,jsx,tsx,mdx}',
    './components/**/*.{js,ts,jsx,tsx,mdx}',
  ],
  theme: {
    extend: {
      colors: {
        primary: '#da291c',
        'primary-active': '#b01e0a',
        'primary-hover': '#9d2211',
        canvas: '#181818',
        'canvas-elevated': '#303030',
        'canvas-light': '#ffffff',
        ink: '#ffffff',
        body: '#969696',
        'body-strong': '#ffffff',
        'body-on-light': '#181818',
        muted: '#666666',
        'muted-soft': '#8f8f8f',
        hairline: '#303030',
        'hairline-on-light': '#d2d2d2',
        'surface-card': '#303030',
        'on-primary': '#ffffff',
      },
      fontFamily: {
        sans: ['Inter', '-apple-system', 'system-ui', 'sans-serif'],
        mono: ['JetBrains Mono', 'Fira Code', 'Consolas', 'monospace'],
      },
      fontSize: {
        'display-mega': ['80px', { lineHeight: '1.05', letterSpacing: '-1.6px', fontWeight: '500' }],
        'display-xl': ['56px', { lineHeight: '1.1', letterSpacing: '-1.12px', fontWeight: '500' }],
        'display-lg': ['36px', { lineHeight: '1.2', letterSpacing: '-0.36px', fontWeight: '500' }],
        'display-md': ['26px', { lineHeight: '1.5', letterSpacing: '0.195px', fontWeight: '500' }],
        'title-md': ['18px', { lineHeight: '1.2', fontWeight: '700' }],
        'title-sm': ['16px', { lineHeight: '1.4', letterSpacing: '0.08px', fontWeight: '500' }],
        'body-md': ['14px', { lineHeight: '1.5', fontWeight: '400' }],
        'body-sm': ['13px', { lineHeight: '1.5', fontWeight: '400' }],
        caption: ['12px', { lineHeight: '1.4', fontWeight: '400' }],
        'caption-upper': ['11px', { lineHeight: '1.4', letterSpacing: '1.1px', fontWeight: '600' }],
        'btn': ['14px', { lineHeight: '1.0', letterSpacing: '1.4px', fontWeight: '700' }],
        'nav-link': ['13px', { lineHeight: '1.4', letterSpacing: '0.65px', fontWeight: '600' }],
        'number-display': ['80px', { lineHeight: '1.0', letterSpacing: '-1.6px', fontWeight: '700' }],
      },
      spacing: {
        xxxs: '4px',
        xxs: '8px',
        xs: '16px',
        sm: '24px',
        md: '32px',
        lg: '48px',
        xl: '64px',
        xxl: '96px',
        super: '128px',
      },
      borderRadius: {
        none: '0px',
        xs: '2px',
        sm: '4px',
        md: '6px',
        lg: '8px',
        xl: '12px',
        full: '9999px',
      },
      maxWidth: {
        editorial: '1280px',
      },
      animation: {
        'fade-in-up': 'fadeInUp 0.6s ease forwards',
        'terminal-line': 'terminalLine 0.4s ease forwards',
      },
      keyframes: {
        fadeInUp: {
          '0%': { opacity: '0', transform: 'translateY(16px)' },
          '100%': { opacity: '1', transform: 'translateY(0)' },
        },
        terminalLine: {
          '0%': { opacity: '0', transform: 'translateX(-4px)' },
          '100%': { opacity: '1', transform: 'translateX(0)' },
        },
      },
    },
  },
  plugins: [],
};

export default config;
