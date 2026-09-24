/**
 * DriveForge Web Landing Page - Tailwind Configuration
 */
window.tailwind = window.tailwind || {};
window.tailwind.config = {
  darkMode: 'class',
  theme: {
    extend: {
      fontFamily: {
        sans: ['"Google Sans Flex"', 'Inter', '-apple-system', 'BlinkMacSystemFont', 'system-ui', 'sans-serif'],
        mono: ['"Google Sans Code"', '"JetBrains Mono"', 'monospace'],
      },
      colors: {
        brand: {
          50: '#eef6ff',
          100: '#d9ecff',
          400: '#4da4ff',
          500: '#1a73e8',
          600: '#1557b0',
          accent: '#38bdf8',
          glow: '#60a5fa',
          purple: '#8b5cf6',
          emerald: '#10b981',
          amber: '#f59e0b',
        }
      },
      boxShadow: {
        'glow-blue': '0 0 45px -5px rgba(26, 115, 232, 0.5)',
        'glow-cyan': '0 0 45px -5px rgba(56, 189, 248, 0.5)',
        'glass': '0 8px 32px 0 rgba(0, 0, 0, 0.37)',
        'glass-light': '0 10px 30px -5px rgba(0, 0, 0, 0.08)',
      }
    }
  }
};
