import type { Metadata } from 'next';
import './globals.css';
import Navbar from '@/components/Navbar';

export const metadata: Metadata = {
  title: {
    default: 'Swiggy AI Discovery Engine — Insights Dashboard',
    template: '%s — AI Discovery Engine',
  },
  description: 'Analyzing food delivery user friction — why users abandon carts, cancel orders, or switch to competitor platforms.',
  keywords: ['Swiggy', 'analytics', 'consumer insights', 'discovery engine', 'AI research'],
  authors: [{ name: 'AI Discovery Engine' }],
  openGraph: {
    title: 'Swiggy AI Discovery Engine — Insights Dashboard',
    description: 'Analyzing food delivery user friction — why users abandon carts, cancel orders, or switch to competitor platforms.',
    type: 'website',
    siteName: 'AI Discovery Engine',
  },
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en" data-mode="dark" data-theme="tokyo-sakura" data-scroll-behavior="smooth" suppressHydrationWarning>
      <head>
        <script
          dangerouslySetInnerHTML={{
            __html: `
              (function() {
                try {
                  var m = localStorage.getItem('app-mode') || 'dark';
                  var t = localStorage.getItem('app-theme') || 'tokyo-sakura';
                  if (t === 'sunset') t = 'tokyo-sakura';
                  if (t === 'emerald') t = 'cyber-matrix';
                  if (t === 'nebula') t = 'cosmic-nebula';
                  document.documentElement.setAttribute('data-mode', m);
                  document.documentElement.setAttribute('data-theme', t);
                } catch (e) {}
              })();
            `,
          }}
        />
      </head>
      <body suppressHydrationWarning>
        <Navbar />
        <main className="page-wrapper">
          {children}
        </main>
      </body>
    </html>
  );
}
