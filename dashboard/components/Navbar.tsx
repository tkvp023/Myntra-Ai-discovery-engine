'use client';
import Link from 'next/link';
import { usePathname } from 'next/navigation';
import { useState, useEffect, useRef } from 'react';

const QUESTIONS = [
  { id: 1, short: 'Wishlist Motivation', desc: 'Why users shortlist vs purchase' },
  { id: 2, short: 'Purchase Prevention', desc: 'Core friction & blocker tags' },
  { id: 3, short: 'Remaining Uncertainties', desc: 'Fit, fabric & quality anxiety' },
  { id: 4, short: 'Purchase Postponement', desc: 'Sale waiting & price drops' },
  { id: 5, short: 'Comparison Behavior', desc: 'Amazon, Ajio & Meesho comparison' },
  { id: 6, short: 'External Info Seeking', desc: 'YouTube hauls & Instagram reels' },
  { id: 7, short: 'Factor Importance', desc: 'Fit, price, styling & returns' },
  { id: 8, short: 'Intent vs Bookmarking', desc: 'Immediate buy vs aesthetic saves' },
  { id: 9, short: 'Segment Differences', desc: 'Gen-Z, deal seekers & plus size' },
  { id: 10, short: 'Unmet Needs', desc: 'High-frequency customer feature requests' },
];

export default function Navbar() {
  const pathname = usePathname();
  const [mobileOpen, setMobileOpen] = useState(false);
  const [questionsOpen, setQuestionsOpen] = useState(false);
  const dropdownRef = useRef<HTMLDivElement>(null);

  const isActive = (href: string) => pathname === href || pathname.startsWith(href + '/');

  // Close dropdown on outside click
  useEffect(() => {
    function handleClickOutside(event: MouseEvent) {
      if (dropdownRef.current && !dropdownRef.current.contains(event.target as Node)) {
        setQuestionsOpen(false);
      }
    }
    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);

  // Close mobile nav and dropdown on route change
  useEffect(() => {
    setMobileOpen(false);
    setQuestionsOpen(false);
  }, [pathname]);

  return (
    <nav className="navbar" role="navigation" aria-label="Main navigation">
      <Link href="/" className="navbar-logo">
        AI Discovery Engine
      </Link>

      {/* Hamburger (mobile only) */}
      <button
        className="navbar-hamburger"
        onClick={() => setMobileOpen(!mobileOpen)}
        aria-label={mobileOpen ? 'Close menu' : 'Open menu'}
        aria-expanded={mobileOpen}
      >
        {mobileOpen ? '✕' : '☰'}
      </button>

      {/* Desktop + Mobile nav */}
      <div className={`navbar-nav ${mobileOpen ? 'mobile-open' : ''}`}>
        <Link href="/" className={`nav-link ${pathname === '/' ? 'active' : ''}`}>
          Summary
        </Link>

        {/* Questions dropdown */}
        <div
          className="nav-dropdown"
          ref={dropdownRef}
          onMouseEnter={() => setQuestionsOpen(true)}
          onMouseLeave={() => setQuestionsOpen(false)}
        >
          <button
            className={`nav-link ${isActive('/questions') ? 'active' : ''}`}
            onClick={(e) => {
              e.preventDefault();
              setQuestionsOpen(!questionsOpen);
            }}
            style={{
              display: 'flex',
              alignItems: 'center',
              gap: 6,
              cursor: 'pointer',
            }}
            aria-expanded={questionsOpen}
            aria-haspopup="true"
          >
            Questions
            <svg
              width="10"
              height="6"
              viewBox="0 0 10 6"
              fill="none"
              xmlns="http://www.w3.org/2000/svg"
              style={{
                transition: 'transform 0.2s ease',
                transform: questionsOpen ? 'rotate(180deg)' : 'rotate(0deg)',
                stroke: 'currentColor',
                strokeWidth: 1.6,
                strokeLinecap: 'round',
                strokeLinejoin: 'round',
              }}
            >
              <path d="M1 1L5 5L9 1" />
            </svg>
          </button>

          {questionsOpen && (
            <div
              className="nav-dropdown-menu"
              style={{
                display: 'grid',
                gridTemplateColumns: '1fr',
                gap: 2,
                minWidth: 280,
                padding: '8px',
                background: 'rgba(15, 15, 28, 0.95)',
                border: '1px solid rgba(255, 255, 255, 0.12)',
                borderRadius: '12px',
                boxShadow: '0 12px 32px rgba(0, 0, 0, 0.6), 0 0 0 1px rgba(255, 63, 108, 0.15)',
                backdropFilter: 'blur(16px)',
                position: 'absolute',
                top: 'calc(100% + 4px)',
                left: 0,
                zIndex: 300,
              }}
              role="menu"
            >
              <div style={{
                padding: '4px 10px 8px 10px',
                borderBottom: '1px solid rgba(255,255,255,0.06)',
                marginBottom: 4,
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'space-between',
              }}>
                <span style={{ fontSize: 11, fontWeight: 700, textTransform: 'uppercase', letterSpacing: '0.08em', color: 'var(--text-muted)' }}>
                  10 Strategic Inquiries
                </span>
                <span style={{ fontSize: 10, background: 'rgba(255,63,108,0.15)', color: 'var(--pink)', padding: '1px 6px', borderRadius: 10, fontWeight: 600 }}>
                  Wishlist Funnel
                </span>
              </div>
              {QUESTIONS.map((q) => {
                const isCurrent = pathname === `/questions/${q.id}`;
                return (
                  <Link
                    key={q.id}
                    href={`/questions/${q.id}`}
                    className="nav-dropdown-item"
                    onClick={() => {
                      setQuestionsOpen(false);
                      setMobileOpen(false);
                    }}
                    style={{
                      display: 'flex',
                      flexDirection: 'column',
                      gap: 2,
                      padding: '8px 10px',
                      borderRadius: '8px',
                      background: isCurrent ? 'rgba(255, 63, 108, 0.12)' : 'transparent',
                      border: isCurrent ? '1px solid rgba(255, 63, 108, 0.3)' : '1px solid transparent',
                      transition: 'all 0.15s ease',
                    }}
                    role="menuitem"
                  >
                    <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
                      <span style={{
                        color: isCurrent ? '#ff3f6c' : 'var(--pink)',
                        fontWeight: 800,
                        fontSize: 12,
                        background: 'rgba(255,63,108,0.1)',
                        padding: '1px 6px',
                        borderRadius: 4,
                        minWidth: 28,
                        textAlign: 'center',
                      }}>
                        Q{q.id}
                      </span>
                      <span style={{ fontWeight: 600, fontSize: 13, color: isCurrent ? '#fff' : 'var(--text-primary)' }}>
                        {q.short}
                      </span>
                    </div>
                    <span style={{ fontSize: 11, color: 'var(--text-muted)', marginLeft: 36 }}>
                      {q.desc}
                    </span>
                  </Link>
                );
              })}
            </div>
          )}
        </div>

        <Link href="/gaps" className={`nav-link ${isActive('/gaps') ? 'active' : ''}`}>
          Systemic Gaps
        </Link>

        <Link href="/ask" className={`nav-link ${isActive('/ask') ? 'active' : ''}`}>
          Ask AI
        </Link>
      </div>

      {/* Corpus status pill */}
      <div
        title="Live dataset aggregated across YouTube, Play Store, Reddit, App Store, and PissedConsumer"
        style={{
          marginLeft: 'auto',
          display: 'flex',
          alignItems: 'center',
          gap: 8,
          background: 'rgba(16, 185, 129, 0.1)',
          border: '1px solid rgba(16, 185, 129, 0.25)',
          borderRadius: 20,
          padding: '5px 14px',
          fontSize: 12,
          color: '#10b981',
          fontWeight: 600,
          whiteSpace: 'nowrap',
          boxShadow: '0 0 12px rgba(16, 185, 129, 0.15)',
        }}
      >
        <span
          style={{
            width: 7,
            height: 7,
            borderRadius: '50%',
            background: '#10b981',
            display: 'inline-block',
            boxShadow: '0 0 8px #10b981',
          }}
        />
        Live Corpus (8,182 Reviews)
      </div>
    </nav>
  );
}
