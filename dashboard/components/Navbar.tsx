'use client';
import Link from 'next/link';
import { usePathname } from 'next/navigation';
import { useState, useEffect, useRef } from 'react';
import ThemeControls from '@/components/ThemeControls';

const QUESTIONS = [
  { id: 1, group: 'funnel', short: 'Wishlist Motivation', desc: 'Why users shortlist vs purchase' },
  { id: 2, group: 'funnel', short: 'Purchase Prevention', desc: 'Core friction & blocker tags' },
  { id: 3, group: 'funnel', short: 'Remaining Uncertainties', desc: 'Fit, fabric & quality anxiety' },
  { id: 4, group: 'funnel', short: 'Purchase Postponement', desc: 'Sale waiting & price drops' },
  { id: 5, group: 'funnel', short: 'Comparison Behavior', desc: 'Amazon, Ajio & Meesho comparison' },
  { id: 6, group: 'dynamics', short: 'External Info Seeking', desc: 'YouTube hauls & Instagram reels' },
  { id: 7, group: 'dynamics', short: 'Factor Importance', desc: 'Fit, price, styling & returns' },
  { id: 8, group: 'dynamics', short: 'Intent vs Bookmarking', desc: 'Immediate buy vs aesthetic saves' },
  { id: 9, group: 'dynamics', short: 'Segment Differences', desc: 'Inferred behavioral segments' },
  { id: 10, group: 'dynamics', short: 'Unmet Needs', desc: 'High-frequency customer feature requests' },
];

export default function Navbar() {
  const pathname = usePathname();
  const [mobileOpen, setMobileOpen] = useState(false);
  const [questionsOpen, setQuestionsOpen] = useState(false);
  const dropdownRef = useRef<HTMLDivElement>(null);
  const timeoutRef = useRef<NodeJS.Timeout | null>(null);

  const isActive = (href: string) => pathname === href || pathname.startsWith(href + '/');

  const handleMouseEnter = () => {
    if (timeoutRef.current) {
      clearTimeout(timeoutRef.current);
      timeoutRef.current = null;
    }
    setQuestionsOpen(true);
  };

  const handleMouseLeave = () => {
    if (timeoutRef.current) clearTimeout(timeoutRef.current);
    // 250ms grace period so accidental mouse slips do not close the menu
    timeoutRef.current = setTimeout(() => {
      setQuestionsOpen(false);
    }, 250);
  };

  // Close dropdown on outside click
  useEffect(() => {
    function handleClickOutside(event: MouseEvent) {
      if (dropdownRef.current && !dropdownRef.current.contains(event.target as Node)) {
        setQuestionsOpen(false);
      }
    }
    document.addEventListener('mousedown', handleClickOutside);
    return () => {
      document.removeEventListener('mousedown', handleClickOutside);
      if (timeoutRef.current) clearTimeout(timeoutRef.current);
    };
  }, []);

  // Close mobile nav and dropdown on route change
  useEffect(() => {
    setMobileOpen(false);
    setQuestionsOpen(false);
  }, [pathname]);

  // Keyboard navigation support
  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Escape') {
      setQuestionsOpen(false);
    } else if (e.key === 'ArrowDown' && !questionsOpen) {
      setQuestionsOpen(true);
    }
  };

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
          onMouseEnter={handleMouseEnter}
          onMouseLeave={handleMouseLeave}
          onKeyDown={handleKeyDown}
        >
          <button
            className={`nav-link ${isActive('/questions') ? 'active' : ''}`}
            onClick={(e) => {
              e.preventDefault();
              setQuestionsOpen((prev) => !prev);
            }}
            style={{
              display: 'inline-flex',
              alignItems: 'center',
              gap: 6,
              cursor: 'pointer',
              fontWeight: 500,
            }}
            aria-expanded={questionsOpen}
            aria-haspopup="true"
            aria-controls="questions-mega-menu"
            id="questions-menu-button"
          >
            <span>Questions</span>
            <svg
              width="10"
              height="6"
              viewBox="0 0 10 6"
              fill="none"
              xmlns="http://www.w3.org/2000/svg"
              style={{
                transition: 'transform 0.2s cubic-bezier(0.4, 0, 0.2, 1)',
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

          {/* Invisible hover safety bridge */}
          {questionsOpen && (
            <div
              id="questions-mega-menu"
              className="nav-dropdown-menu mega-menu"
              style={{
                display: 'block',
                width: '560px',
                maxWidth: 'calc(100vw - 32px)',
                padding: '12px',
                background: 'var(--dropdown-bg)',
                border: '1px solid var(--border-strong)',
                borderRadius: '16px',
                boxShadow: 'var(--shadow-card), 0 0 24px var(--theme-accent-border)',
                backdropFilter: 'var(--glass-blur)',
                WebkitBackdropFilter: 'var(--glass-blur)',
                position: 'absolute',
                top: '100%',
                left: 0,
                marginTop: '6px',
                zIndex: 300,
                animation: 'fadeSlideUp 0.18s cubic-bezier(0.16, 1, 0.3, 1)',
              }}
              role="menu"
              aria-labelledby="questions-menu-button"
            >
              {/* Header banner */}
              <div
                style={{
                  padding: '4px 10px 10px 10px',
                  borderBottom: '1px solid var(--border)',
                  marginBottom: 10,
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'space-between',
                }}
              >
                <div style={{ display: 'flex', alignItems: 'center', gap: 6 }}>
                  <span style={{ fontSize: 13 }}>📊</span>
                  <span style={{ fontSize: 12, fontWeight: 700, textTransform: 'uppercase', letterSpacing: '0.06em', color: 'var(--text-primary)' }}>
                    10 Strategic Inquiries
                  </span>
                </div>
                <span
                  style={{
                    fontSize: 11,
                    background: 'var(--theme-accent-bg)',
                    color: 'var(--pink)',
                    border: '1px solid var(--theme-accent-border)',
                    padding: '2px 8px',
                    borderRadius: 12,
                    fontWeight: 600,
                  }}
                >
                  Wishlist Intelligence
                </span>
              </div>

              {/* 2-Column Grid */}
              <div
                style={{
                  display: 'grid',
                  gridTemplateColumns: 'repeat(auto-fit, minmax(240px, 1fr))',
                  gap: 6,
                }}
              >
                {QUESTIONS.map((q) => {
                  const isCurrent = pathname === `/questions/${q.id}`;
                  return (
                    <Link
                      key={q.id}
                      href={`/questions/${q.id}`}
                      className="nav-dropdown-item question-nav-item"
                      onClick={() => {
                        setQuestionsOpen(false);
                        setMobileOpen(false);
                      }}
                      style={{
                        display: 'flex',
                        alignItems: 'flex-start',
                        gap: 10,
                        padding: '9px 10px',
                        borderRadius: '10px',
                        background: isCurrent ? 'var(--theme-accent-bg)' : 'transparent',
                        border: isCurrent ? '1px solid var(--theme-accent-border)' : '1px solid transparent',
                        transition: 'all 0.15s ease',
                        textDecoration: 'none',
                        cursor: 'pointer',
                      }}
                      role="menuitem"
                    >
                      <span
                        style={{
                          color: isCurrent ? '#fff' : 'var(--pink)',
                          fontWeight: 800,
                          fontSize: 11,
                          background: isCurrent ? 'var(--pink)' : 'var(--theme-accent-bg)',
                          padding: '2px 6px',
                          borderRadius: 6,
                          minWidth: 26,
                          textAlign: 'center',
                          marginTop: 1,
                          flexShrink: 0,
                        }}
                      >
                        Q{q.id}
                      </span>
                      <div style={{ display: 'flex', flexDirection: 'column', gap: 2 }}>
                        <span
                          style={{
                            fontWeight: 600,
                            fontSize: 13,
                            color: isCurrent ? 'var(--pink)' : 'var(--text-primary)',
                            lineHeight: 1.3,
                          }}
                        >
                          {q.short}
                        </span>
                        <span
                          style={{
                            fontSize: 11,
                            color: 'var(--text-secondary)',
                            lineHeight: 1.3,
                          }}
                        >
                          {q.desc}
                        </span>
                      </div>
                    </Link>
                  );
                })}
              </div>
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

      {/* Right controls: Theme + Mode & Corpus status */}
      <div style={{ marginLeft: 'auto', display: 'flex', alignItems: 'center', gap: 12 }}>
        <ThemeControls />

        <div
          className="corpus-status-badge"
          title="Live dataset aggregated across YouTube, Play Store, Reddit, App Store, and PissedConsumer"
          style={{
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
      </div>
    </nav>
  );
}
