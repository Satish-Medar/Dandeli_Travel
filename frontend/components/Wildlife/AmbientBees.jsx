"use client";

import { useEffect, useState } from "react";

export default function AmbientBees() {
  const [mounted, setMounted] = useState(false);
  
  useEffect(() => {
    setMounted(true);
  }, []);

  if (!mounted) return null;

  const bees = [
    { id: 1, top: '20%', left: '10%', delay: '0s', scale: 0.8 },
    { id: 2, top: '45%', left: '85%', delay: '1.2s', scale: 1.2 },
    { id: 3, top: '80%', left: '20%', delay: '2.5s', scale: 0.9 },
    { id: 4, top: '90%', left: '80%', delay: '0.8s', scale: 1.1 },
    { id: 5, top: '15%', left: '70%', delay: '3.1s', scale: 0.7 },
  ];

  return (
    <div style={{ position: 'absolute', top: 0, left: 0, width: '100%', height: '100%', pointerEvents: 'none', zIndex: 10 }}>
      {bees.map(bee => (
        <div 
          key={bee.id} 
          className="ambient-bee" 
          style={{ 
            top: bee.top, 
            left: bee.left, 
            animationDelay: bee.delay,
            transform: `scale(${bee.scale})`
          }}
        >
          <svg width="24" height="24" viewBox="0 0 100 100">
            {/* Body */}
            <ellipse cx="50" cy="60" rx="15" ry="25" fill="#f59e0b" transform="rotate(45 50 60)" />
            {/* Stripes */}
            <path d="M40 45 L65 70" stroke="#1f2937" strokeWidth="6" strokeLinecap="round" />
            <path d="M30 55 L55 80" stroke="#1f2937" strokeWidth="6" strokeLinecap="round" />
            {/* Wings */}
            <path className="bee-wing-l" d="M40 50 C20 10, 50 10, 45 45 Z" fill="#9ca3af" opacity="0.6" />
            <path className="bee-wing-r" d="M60 70 C90 90, 90 60, 55 65 Z" fill="#9ca3af" opacity="0.6" />
          </svg>
        </div>
      ))}
    </div>
  );
}
