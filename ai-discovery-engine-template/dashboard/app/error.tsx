'use client';

import { useEffect } from 'react';

export default function GlobalError({
  error,
  reset,
}: {
  error: Error & { digest?: string };
  reset: () => void;
}) {
  useEffect(() => {
    console.error('Dashboard error:', error);
  }, [error]);

  return (
    <div className="container" style={{ paddingTop: 80, paddingBottom: 64 }}>
      <div className="card" style={{
        maxWidth: 560,
        margin: '0 auto',
        borderColor: 'rgba(255,63,108,0.3)',
        textAlign: 'center',
      }}>
        <div className="card-body" style={{ padding: '48px 32px' }}>
          {/* Error icon */}
          <div style={{
            width: 64, height: 64, borderRadius: '50%',
            background: 'rgba(255,63,108,0.1)',
            display: 'flex', alignItems: 'center', justifyContent: 'center',
            margin: '0 auto 20px',
            fontSize: 28,
          }}>
            ⚠️
          </div>

          <h2 style={{
            fontSize: 22, fontWeight: 700, fontFamily: 'Outfit, sans-serif',
            color: 'var(--text-primary)', marginBottom: 8,
          }}>
            Something went wrong
          </h2>

          <p style={{ fontSize: 14, color: 'var(--text-muted)', marginBottom: 24, lineHeight: 1.6 }}>
            An error occurred while rendering this page. This could be due to a data loading issue or a temporary glitch.
          </p>

          {/* Error details (collapsed) */}
          <details style={{
            textAlign: 'left',
            marginBottom: 24,
            background: 'rgba(255,255,255,0.02)',
            borderRadius: 'var(--radius-sm)',
            padding: '10px 14px',
            border: '1px solid var(--border)',
          }}>
            <summary style={{ fontSize: 12, color: 'var(--text-muted)', cursor: 'pointer', fontWeight: 600 }}>
              Error details
            </summary>
            <pre style={{
              fontSize: 11, color: 'var(--pink)', marginTop: 8,
              whiteSpace: 'pre-wrap', wordBreak: 'break-all',
              fontFamily: 'monospace',
            }}>
              {error.message}
            </pre>
            {error.digest && (
              <p style={{ fontSize: 11, color: 'var(--text-muted)', marginTop: 4 }}>
                Digest: {error.digest}
              </p>
            )}
          </details>

          {/* Actions */}
          <div style={{ display: 'flex', gap: 12, justifyContent: 'center' }}>
            <button
              onClick={reset}
              style={{
                background: 'var(--gradient-brand)',
                border: 'none', borderRadius: 'var(--radius-md)',
                color: '#fff', padding: '10px 24px', fontSize: 14,
                fontWeight: 700, cursor: 'pointer',
              }}
            >
              Try again
            </button>
            <a
              href="/"
              style={{
                background: 'var(--glass-bg)',
                border: '1px solid var(--border)',
                borderRadius: 'var(--radius-md)',
                color: 'var(--text-secondary)', padding: '10px 24px',
                fontSize: 14, fontWeight: 600, textDecoration: 'none',
                display: 'inline-flex', alignItems: 'center',
              }}
            >
              ← Back to Summary
            </a>
          </div>
        </div>
      </div>
    </div>
  );
}
