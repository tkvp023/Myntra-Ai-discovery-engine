'use client';
import { useEffect, useState } from 'react';

type Mode = 'dark' | 'light';
type Theme = 'sunset' | 'emerald' | 'nebula';

const THEMES: { id: Theme; name: string; icon: string; preview: string }[] = [
  {
    id: 'sunset',
    name: 'Sunset Coral',
    icon: '🌸',
    preview: 'linear-gradient(135deg, #ff3f6c, #ff7849)',
  },
  {
    id: 'emerald',
    name: 'Cyber Emerald',
    icon: '🌿',
    preview: 'linear-gradient(135deg, #10b981, #06b6d4)',
  },
  {
    id: 'nebula',
    name: 'Royal Nebula',
    icon: '🔮',
    preview: 'linear-gradient(135deg, #8b5cf6, #ec4899)',
  },
];

export default function ThemeControls() {
  const [mounted, setMounted] = useState(false);
  const [mode, setMode] = useState<Mode>('dark');
  const [theme, setTheme] = useState<Theme>('sunset');

  useEffect(() => {
    setMounted(true);
    const initialMode = (document.documentElement.getAttribute('data-mode') as Mode) || 
      (localStorage.getItem('app-mode') as Mode) || 'dark';
    const initialTheme = (document.documentElement.getAttribute('data-theme') as Theme) || 
      (localStorage.getItem('app-theme') as Theme) || 'sunset';

    setMode(initialMode);
    setTheme(initialTheme);
    document.documentElement.setAttribute('data-mode', initialMode);
    document.documentElement.setAttribute('data-theme', initialTheme);
  }, []);

  const toggleMode = () => {
    const nextMode: Mode = mode === 'dark' ? 'light' : 'dark';
    setMode(nextMode);
    document.documentElement.setAttribute('data-mode', nextMode);
    localStorage.setItem('app-mode', nextMode);
    window.dispatchEvent(new Event('theme-change'));
  };

  const selectTheme = (newTheme: Theme) => {
    setTheme(newTheme);
    document.documentElement.setAttribute('data-theme', newTheme);
    localStorage.setItem('app-theme', newTheme);
    window.dispatchEvent(new Event('theme-change'));
  };

  if (!mounted) {
    return (
      <div style={{ display: 'flex', alignItems: 'center', gap: 8, height: 34, minWidth: 160 }} />
    );
  }

  return (
    <div
      className="theme-controls-wrapper"
      style={{
        display: 'flex',
        alignItems: 'center',
        gap: 8,
        background: 'var(--bg-card)',
        border: '1px solid var(--border)',
        borderRadius: 24,
        padding: '3px 8px',
        backdropFilter: 'var(--glass-blur)',
      }}
    >
      {/* 3 Unique Theme Palette Swatches */}
      <div style={{ display: 'flex', alignItems: 'center', gap: 4 }}>
        {THEMES.map((t) => {
          const isSelected = theme === t.id;
          return (
            <button
              key={t.id}
              onClick={() => selectTheme(t.id)}
              title={`${t.name} Theme (${t.icon})`}
              aria-label={`${t.name} color theme`}
              style={{
                width: 20,
                height: 20,
                borderRadius: '50%',
                background: t.preview,
                border: isSelected ? '2px solid #ffffff' : '1px solid rgba(255,255,255,0.2)',
                boxShadow: isSelected ? '0 0 10px rgba(0,0,0,0.5), 0 0 0 2px var(--brand-primary)' : 'none',
                transform: isSelected ? 'scale(1.15)' : 'scale(1)',
                cursor: 'pointer',
                transition: 'all 0.2s cubic-bezier(0.4, 0, 0.2, 1)',
                outline: 'none',
                padding: 0,
              }}
            />
          );
        })}
      </div>

      <div style={{ width: 1, height: 16, background: 'var(--border)', margin: '0 2px' }} />

      {/* Dark / Light Mode Toggle */}
      <button
        onClick={toggleMode}
        title={mode === 'dark' ? 'Switch to Light Mode' : 'Switch to Dark Mode'}
        aria-label={`Switch to ${mode === 'dark' ? 'Light' : 'Dark'} mode`}
        style={{
          background: 'none',
          border: 'none',
          cursor: 'pointer',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          width: 26,
          height: 26,
          borderRadius: '50%',
          color: 'var(--text-primary)',
          transition: 'background 0.2s ease, transform 0.2s ease',
          fontSize: 14,
        }}
        onMouseEnter={(e) => (e.currentTarget.style.transform = 'rotate(15deg) scale(1.1)')}
        onMouseLeave={(e) => (e.currentTarget.style.transform = 'rotate(0deg) scale(1)')}
      >
        {mode === 'dark' ? '🌙' : '☀️'}
      </button>
    </div>
  );
}
