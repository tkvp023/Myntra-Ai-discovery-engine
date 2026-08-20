import type { Metadata } from 'next';
import './globals.css';
import Navbar from '@/components/Navbar';

export const metadata: Metadata = {
  title: {
    default: 'AI Discovery Engine — Myntra Insights Dashboard',
    template: '%s — AI Discovery Engine',
  },
  description: 'Quantified analysis of 87,000+ user reviews revealing why shoppers add to wishlist but hesitate to buy on Myntra.',
  keywords: ['Myntra', 'fashion analytics', 'wishlist behavior', 'consumer insights', 'e-commerce research', 'sizing uncertainty', 'price sensitivity'],
  authors: [{ name: 'AI Discovery Engine' }],
  openGraph: {
    title: 'AI Discovery Engine — Myntra Insights Dashboard',
    description: 'Deep-dive into 87K+ reviews: sizing uncertainty, price sensitivity, and 10 strategic questions answered with data.',
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
