'use client';
import { useEffect, useState } from 'react';

type Mode = 'dark' | 'light';
export type Theme = 'tokyo-sakura' | 'cyber-matrix' | 'cosmic-nebula' | 'solar-flare';

export const THEMES: { id: Theme; name: string; tag: string; icon: string; preview: string; glow: string }[] = [
  {
    id: 'tokyo-sakura',
    name: 'Tokyo Sakura',
    tag: 'Hot Pink & Amber',
    icon: '🌸',
    preview: 'linear-gradient(135deg, #ff2d55, #ff9500)',
    glow: 'rgba(255, 45, 85, 0.4)',
  },
  {
    id: 'cyber-matrix',
    name: 'Cyber Matrix',
    tag: 'Neon Mint & Cyan',
    icon: '⚡',
    preview: 'linear-gradient(135deg, #00f5d4, #00bbf9)',
    glow: 'rgba(0, 245, 212, 0.4)',
  },
  {
    id: 'cosmic-nebula',
    name: 'Cosmic Nebula',
    tag: 'Ultra Violet & Fuchsia',
    icon: '🔮',
    preview: 'linear-gradient(135deg, #8b5cf6, #ec4899)',
    glow: 'rgba(139, 92, 246, 0.4)',
  },
  {
    id: 'solar-flare',
    name: 'Solar Flare',
    tag: 'Molten Ruby & Gold',
    icon: '🔥',
    preview: 'linear-gradient(135deg, #ff3838, #ffb300)',
    glow: 'rgba(255, 56, 56, 0.4)',
  },
];

export default function ThemeControls() {
  const [mounted, setMounted] = useState(false);
  const [mode, setMode] = useState<Mode>('dark');
  const [theme, setTheme] = useState<Theme>('tokyo-sakura');

  useEffect(() => {
    setMounted(true);
    const initialMode = (document.documentElement.getAttribute('data-mode') as Mode) || 
      (localStorage.getItem('app-mode') as Mode) || 'dark';
    
    // Map legacy 'sunset' / 'emerald' / 'nebula' if stored
    let initialTheme = (document.documentElement.getAttribute('data-theme') as string) || 
      localStorage.getItem('app-theme') || 'tokyo-sakura';
    if (initialTheme === 'sunset') initialTheme = 'tokyo-sakura';
    if (initialTheme === 'emerald') initialTheme = 'cyber-matrix';
    if (initialTheme === 'nebula') initialTheme = 'cosmic-nebula';

    setMode(initialMode);
    setTheme(initialTheme as Theme);
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
      <div style={{ display: 'flex', alignItems: 'center', gap: 8, height: 34, minWidth: 190 }} />
    );
  }

  const currentThemeObj = THEMES.find((t) => t.id === theme) || THEMES[0];

  return (
    <div
      className="theme-controls-wrapper"
      style={{
        display: 'flex',
        alignItems: 'center',
        gap: 8,
        background: 'var(--bg-card)',
        border: '1px solid var(--border-strong)',
        borderRadius: 24,
        padding: '3px 10px',
        backdropFilter: 'var(--glass-blur)',
        boxShadow: '0 2px 12px rgba(0,0,0,0.1)',
      }}
    >
      {/* 4 Eye-Catching Theme Swatches with glowing rings */}
      <div style={{ display: 'flex', alignItems: 'center', gap: 6 }}>
        {THEMES.map((t) => {
          const isSelected = theme === t.id;
          return (
            <button
              key={t.id}
              onClick={() => selectTheme(t.id)}
              title={`${t.name} — ${t.tag} (${t.icon})`}
              aria-label={`${t.name} theme`}
              style={{
                width: 22,
                height: 22,
                borderRadius: '50%',
                background: t.preview,
                border: isSelected ? '2px solid #ffffff' : '1px solid rgba(255,255,255,0.25)',
                boxShadow: isSelected
                  ? `0 0 14px ${t.glow}, 0 0 0 2px var(--brand-primary)`
                  : '0 1px 4px rgba(0,0,0,0.2)',
                transform: isSelected ? 'scale(1.22)' : 'scale(1)',
                cursor: 'pointer',
                transition: 'all 0.22s cubic-bezier(0.34, 1.56, 0.64, 1)',
                outline: 'none',
                padding: 0,
                position: 'relative',
              }}
            />
          );
        })}
      </div>

      <div style={{ width: 1, height: 16, background: 'var(--border)', margin: '0 2px' }} />

      {/* Mode Switch Button (🌙 / ☀️) */}
      <button
        onClick={toggleMode}
        title={mode === 'dark' ? 'Switch to Daylight Light Mode' : 'Switch to Midnight Dark Mode'}
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
          transition: 'all 0.2s cubic-bezier(0.4, 0, 0.2, 1)',
          fontSize: 14,
        }}
        onMouseEnter={(e) => {
          e.currentTarget.style.transform = 'rotate(20deg) scale(1.15)';
        }}
        onMouseLeave={(e) => {
          e.currentTarget.style.transform = 'rotate(0deg) scale(1)';
        }}
      >
        {mode === 'dark' ? '🌙' : '☀️'}
      </button>
    </div>
  );
}
