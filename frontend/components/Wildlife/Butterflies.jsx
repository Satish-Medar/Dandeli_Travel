"use client";

import { useEffect, useState } from "react";

export default function Butterflies() {
  const [mousePos, setMousePos] = useState({ x: 0, y: 0 });

  useEffect(() => {
    const handleMouseMove = (e) => {
      setMousePos({ x: e.clientX, y: e.clientY });
    };

    window.addEventListener("mousemove", handleMouseMove);

    return () => {
      window.removeEventListener("mousemove", handleMouseMove);
    };
  }, []);

  return (
    <div style={{ position: 'fixed', top: 0, left: 0, width: '100%', height: '100%', pointerEvents: 'none', zIndex: 100 }}>
      {/* Primary Butterfly */}
      <div 
        className="butterfly" 
        style={{ 
          transform: `translate(${mousePos.x + 20}px, ${mousePos.y + 20}px)`,
          transitionDelay: '0.05s'
        }}
      >
        <svg width="30" height="30" viewBox="0 0 100 100" fill="#10b981">
          <path className="butterfly-wing" d="M50 50 C20 0, 0 30, 45 50 C0 70, 20 100, 50 50 C80 100, 100 70, 55 50 C100 30, 80 0, 50 50 Z" />
        </svg>
      </div>

      {/* Trailing Butterfly 1 */}
      <div 
        className="butterfly" 
        style={{ 
          transform: `translate(${mousePos.x - 30}px, ${mousePos.y + 40}px) scale(0.7)`,
          transitionDelay: '0.15s'
        }}
      >
        <svg width="30" height="30" viewBox="0 0 100 100" fill="#34d399">
          <path className="butterfly-wing" d="M50 50 C20 0, 0 30, 45 50 C0 70, 20 100, 50 50 C80 100, 100 70, 55 50 C100 30, 80 0, 50 50 Z" />
        </svg>
      </div>

      {/* Trailing Butterfly 2 */}
      <div 
        className="butterfly" 
        style={{ 
          transform: `translate(${mousePos.x + 40}px, ${mousePos.y - 10}px) scale(0.5)`,
          transitionDelay: '0.25s'
        }}
      >
        <svg width="30" height="30" viewBox="0 0 100 100" fill="#047857">
          <path className="butterfly-wing" d="M50 50 C20 0, 0 30, 45 50 C0 70, 20 100, 50 50 C80 100, 100 70, 55 50 C100 30, 80 0, 50 50 Z" />
        </svg>
      </div>
    </div>
  );
}
