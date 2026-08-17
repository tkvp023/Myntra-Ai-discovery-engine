import Link from 'next/link';
import type { Metadata } from 'next';

export const metadata: Metadata = {
  title: '404 — Page Not Found',
};

export default function NotFound() {
  return (
    <div className="container" style={{ paddingTop: 80, paddingBottom: 64 }}>
      <div style={{
        maxWidth: 520,
        margin: '0 auto',
        textAlign: 'center',
      }}>
        {/* Big 404 */}
        <div style={{
          fontSize: 96, fontFamily: 'Outfit, sans-serif', fontWeight: 800,
          background: 'var(--gradient-brand)',
          WebkitBackgroundClip: 'text',
          WebkitTextFillColor: 'transparent',
          lineHeight: 1, marginBottom: 16,
        }}>
          404
        </div>

        <h1 style={{
          fontSize: 24, fontWeight: 700, fontFamily: 'Outfit, sans-serif',
          color: 'var(--text-primary)', marginBottom: 8,
        }}>
          Page not found
        </h1>

        <p style={{ fontSize: 14, color: 'var(--text-muted)', marginBottom: 36, lineHeight: 1.6 }}>
          This page doesn&apos;t exist or may have been moved. Try one of the links below to get back on track.
        </p>

        {/* Quick navigation */}
        <div style={{
          display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(140px, 1fr))',
          gap: 12, maxWidth: 440, margin: '0 auto',
        }}>
          {[
            { href: '/', label: 'Summary', icon: '📊' },
            { href: '/questions/1', label: 'Questions', icon: '❓' },
            { href: '/gaps', label: 'Systemic Gaps', icon: '🔍' },
            { href: '/ask', label: 'Ask the Data', icon: '💬' },
          ].map((item) => (
            <Link
              key={item.href}
              href={item.href}
              style={{
                display: 'flex', flexDirection: 'column', alignItems: 'center', gap: 8,
                padding: '20px 16px',
                background: 'var(--glass-bg)',
                border: '1px solid var(--border)',
                borderRadius: 'var(--radius-md)',
                textDecoration: 'none',
                color: 'var(--text-secondary)',
                fontSize: 13, fontWeight: 600,
                transition: 'border-color 0.15s, background 0.15s',
              }}
            >
              <span style={{ fontSize: 24 }}>{item.icon}</span>
              {item.label}
            </Link>
          ))}
        </div>
      </div>
    </div>
  );
}
