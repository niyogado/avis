import React from 'react';

/**
 * Small icon set used across the app.
 * These are inline SVGs to avoid external icon dependencies.
 * Sizes and colors are tuned to match AVIS design tokens.
 */

export function Icon({ name, size = 18, className = '', title }) {
  const common = { width: size, height: size, viewBox: '0 0 24 24', fill: 'none', xmlns: 'http://www.w3.org/2000/svg' };

  switch (name) {
    case 'dashboard':
      return (
        <svg {...common} className={className} aria-hidden>
          <rect x="3" y="3" width="8" height="8" rx="1.5" fill="var(--accent)" />
          <rect x="13" y="3" width="8" height="5" rx="1.5" fill="currentColor" opacity="0.12" />
          <rect x="13" y="10" width="8" height="11" rx="1.5" fill="currentColor" opacity="0.06" />
        </svg>
      );
    case 'profile':
      return (
        <svg {...common} className={className} aria-hidden>
          <circle cx="12" cy="8" r="3.2" fill="currentColor" opacity="0.12" />
          <path d="M4 20c0-3.3 4-5 8-5s8 1.7 8 5" stroke="currentColor" strokeWidth="1.2" strokeLinecap="round" strokeLinejoin="round" />
        </svg>
      );
    case 'cv':
      return (
        <svg {...common} className={className} aria-hidden>
          <rect x="4" y="3" width="16" height="18" rx="2" stroke="currentColor" strokeWidth="1.2" />
          <path d="M8 7h8M8 11h8M8 15h5" stroke="currentColor" strokeWidth="1.2" strokeLinecap="round" />
        </svg>
      );
    case 'chat':
      return (
        <svg {...common} className={className} aria-hidden>
          <path d="M21 15a2 2 0 0 1-2 2H8l-5 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z" stroke="currentColor" strokeWidth="1.2" fill="none" />
        </svg>
      );
    case 'jobs':
      return (
        <svg {...common} className={className} aria-hidden>
          <rect x="3" y="7" width="18" height="12" rx="2" stroke="currentColor" strokeWidth="1.2" fill="none" />
          <path d="M8 7V5a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2" stroke="currentColor" strokeWidth="1.2" />
        </svg>
      );
    case 'alerts':
      return (
        <svg {...common} className={className} aria-hidden>
          <path d="M12 22a2.5 2.5 0 0 0 2.5-2.5h-5A2.5 2.5 0 0 0 12 22z" fill="currentColor" opacity="0.12" />
          <path d="M18 14v-3a6 6 0 1 0-12 0v3l-2 2v1h16v-1l-2-2z" stroke="currentColor" strokeWidth="1.2" fill="none" />
        </svg>
      );
    case 'logout':
      return (
        <svg {...common} className={className} aria-hidden>
          <path d="M16 17l5-5-5-5" stroke="currentColor" strokeWidth="1.4" strokeLinecap="round" strokeLinejoin="round" fill="none" />
          <path d="M21 12H9" stroke="currentColor" strokeWidth="1.4" strokeLinecap="round" strokeLinejoin="round" fill="none" />
          <path d="M13 19H6a2 2 0 0 1-2-2V7a2 2 0 0 1 2-2h7" stroke="currentColor" strokeWidth="1.4" strokeLinecap="round" strokeLinejoin="round" fill="none" />
        </svg>
      );
    case 'google':
      return (
        <svg {...common} className={className} aria-hidden>
          <path d="M21 12.3c0-.7-.1-1.3-.3-1.9H12v3.6h5.5c-.2 1.1-.9 2-1.9 2.6v2.1h3.1c1.8-1.6 2.8-4 2.8-6.4z" fill="#4285F4" />
          <path d="M12 22c2.7 0 5-0.9 6.7-2.4l-3.1-2.1c-.9.6-2.1.9-3.6.9-2.8 0-5.1-1.9-5.9-4.5H3.8v2.8C5.6 19.9 8.6 22 12 22z" fill="#34A853" />
          <path d="M6.1 13.9A6.9 6.9 0 0 1 6 12c0-.9.2-1.7.6-2.5V6.7H3.8A10 10 0 0 0 2 12c0 1.6.4 3.1 1.1 4.4l2.9-2.5z" fill="#FBBC05" />
          <path d="M12 6.1c1.5 0 2.8.5 3.8 1.5l2.8-2.8C17 3.4 14.7 2.5 12 2.5 8.6 2.5 5.6 4.6 3.8 7.7l2.9 2.2C6.9 7.9 9.2 6.1 12 6.1z" fill="#EA4335" />
        </svg>
      );
    case 'microsoft':
      return (
        <svg {...common} className={className} aria-hidden>
          <rect x="3" y="3" width="8" height="8" fill="#F35325" />
          <rect x="13" y="3" width="8" height="8" fill="#81BC06" />
          <rect x="3" y="13" width="8" height="8" fill="#05A6F0" />
          <rect x="13" y="13" width="8" height="8" fill="#FFBA08" />
        </svg>
      );
    case 'apple':
      return (
        <svg {...common} className={className} aria-hidden>
          <path d="M16.365 1.43c-.9.1-2.1.6-2.8 1.4-.6.7-1.2 1.8-1 2.8 1.1.1 2.3-.6 3-1.4.6-.7 1.1-1.8.8-2.8z" fill="currentColor" />
          <path d="M12 6.5c-2.8 0-4.6 1.9-4.6 4.6 0 2.6 1.8 4.6 4.6 4.6 2.8 0 4.6-1.9 4.6-4.6C16.6 8.4 14.8 6.5 12 6.5z" fill="currentColor" />
        </svg>
      );
    case 'linkedin':
      return (
        <svg {...common} className={className} aria-hidden>
          <rect x="2" y="2" width="20" height="20" rx="2" fill="#0A66C2" />
          <path d="M7 10v7H4v-7h3zM5.5 8.5a1.5 1.5 0 1 1 0-3 1.5 1.5 0 0 1 0 3zM14 10c1.7 0 2.8.9 3.2 2.1V10h3v7h-3v-3.6c0-1.1-.4-1.8-1.4-1.8-.8 0-1.3.5-1.5 1-.1.2-.1.5-.1.8V17h-3v-7h3z" fill="#fff" />
        </svg>
      );
    default:
      return <svg {...common} className={className} aria-hidden><rect width="24" height="24" fill="currentColor" opacity="0.06" /></svg>;
  }
}
