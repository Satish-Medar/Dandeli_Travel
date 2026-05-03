"use client";

export default function TigerGuide() {
  return (
    <div style={{ display: 'flex', alignItems: 'flex-start', gap: '24px', margin: '40px 0', position: 'relative' }}>
      <div className="tiger-guide" style={{ width: '140px', flexShrink: 0, alignSelf: 'center' }}>
        <svg viewBox="0 0 200 200" width="100%" height="100%" style={{ filter: 'drop-shadow(0 10px 15px rgba(0,0,0,0.2))' }}>
          <defs>
            <linearGradient id="tigerGrad" x1="0%" y1="0%" x2="100%" y2="100%">
              <stop offset="0%" stopColor="#f59e0b" />
              <stop offset="100%" stopColor="#d97706" />
            </linearGradient>
            <linearGradient id="tigerDark" x1="0%" y1="0%" x2="100%" y2="100%">
              <stop offset="0%" stopColor="#1f2937" />
              <stop offset="100%" stopColor="#111827" />
            </linearGradient>
          </defs>
          {/* Head Shape */}
          <path d="M40 100 C40 40, 160 40, 160 100 C180 160, 20 160, 40 100 Z" fill="url(#tigerGrad)" />
          {/* Ears */}
          <path d="M40 70 L20 20 L80 50 Z" fill="url(#tigerGrad)" stroke="#1f2937" strokeWidth="4" />
          <path d="M160 70 L180 20 L120 50 Z" fill="url(#tigerGrad)" stroke="#1f2937" strokeWidth="4" />
          {/* Inner Ears */}
          <path d="M45 65 L30 30 L70 55 Z" fill="#fcd34d" />
          <path d="M155 65 L170 30 L130 55 Z" fill="#fcd34d" />
          {/* Bold Stripes */}
          <path d="M80 50 L120 50 L100 70 Z" fill="url(#tigerDark)" />
          <path d="M30 90 L60 85 L45 105 Z" fill="url(#tigerDark)" />
          <path d="M170 90 L140 85 L155 105 Z" fill="url(#tigerDark)" />
          <path d="M40 120 L70 115 L50 135 Z" fill="url(#tigerDark)" />
          <path d="M160 120 L130 115 L150 135 Z" fill="url(#tigerDark)" />
          {/* Eyes (Glowing Green) */}
          <ellipse cx="75" cy="100" rx="12" ry="16" fill="#10b981" />
          <ellipse cx="125" cy="100" rx="12" ry="16" fill="#10b981" />
          <circle cx="75" cy="100" r="5" fill="#1f2937" />
          <circle cx="125" cy="100" r="5" fill="#1f2937" />
          {/* Nose */}
          <path d="M85 130 L115 130 L100 150 Z" fill="#ef4444" />
          {/* Muzzle */}
          <path d="M100 150 C110 160, 120 150, 120 150" stroke="#1f2937" strokeWidth="4" fill="none" strokeLinecap="round" />
          <path d="M100 150 C90 160, 80 150, 80 150" stroke="#1f2937" strokeWidth="4" fill="none" strokeLinecap="round" />
        </svg>
      </div>
      
      <div className="timeline-content tiger-bubble" style={{ position: 'relative', borderRadius: '24px 24px 24px 4px', background: 'var(--forest-dark)', color: 'white', border: 'none', padding: '32px', width: '100%' }}>
        <div style={{ position: 'absolute', left: '-15px', top: '30px', width: 0, height: 0, borderTop: '15px solid transparent', borderBottom: '15px solid transparent', borderRight: '20px solid var(--forest-dark)' }}></div>
        <h3 style={{ color: '#a7f3d0', fontSize: '1.75rem', marginBottom: '16px' }}>Hi, I'm Vana!</h3>
        <p style={{ color: '#ecfdf5', marginBottom: '16px', fontSize: '1.15rem' }}>
          I am your personal AI guide to the Dandeli jungle. I'm not a regular search engine—I'm a 70-Billion parameter intelligent agent.
        </p>
        <p style={{ color: '#ecfdf5', margin: 0, fontSize: '1.15rem' }}>
          Skip the frustrating aggregators. Just chat with me! I'll instantly scour verified local data to find the absolute best resorts and activities for you, and I'll even book them directly via WhatsApp with zero platform fees.
        </p>
      </div>
    </div>
  );
}
