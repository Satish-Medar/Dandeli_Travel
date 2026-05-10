"use client";

import { useEffect, useState } from "react";

const randomPercent = () =>
  Math.max(5, Math.min(95, Math.floor(Math.random() * 90) + 5));
const randomScale = () => Number((0.7 + Math.random() * 0.5).toFixed(2));

const initialButterflies = [
  {
    id: 1,
    top: randomPercent(),
    left: randomPercent(),
    scale: randomScale(),
    color: "#10b981",
    delay: 0,
  },
  {
    id: 2,
    top: randomPercent(),
    left: randomPercent(),
    scale: randomScale(),
    color: "#34d399",
    delay: 150,
  },
  {
    id: 3,
    top: randomPercent(),
    left: randomPercent(),
    scale: randomScale(),
    color: "#047857",
    delay: 300,
  },
];

export default function Butterflies() {
  const [butterflies, setButterflies] = useState(initialButterflies);

  useEffect(() => {
    const interval = window.setInterval(() => {
      setButterflies((current) =>
        current.map((butterfly) => ({
          ...butterfly,
          top: randomPercent(),
          left: randomPercent(),
          scale: randomScale(),
        })),
      );
    }, 3000);

    return () => window.clearInterval(interval);
  }, []);

  return (
    <div
      style={{
        position: "fixed",
        top: 0,
        left: 0,
        width: "100%",
        height: "100%",
        pointerEvents: "none",
        zIndex: 100,
      }}
    >
      {butterflies.map((butterfly) => (
        <div
          key={butterfly.id}
          className="butterfly"
          style={{
            position: "absolute",
            top: `${butterfly.top}%`,
            left: `${butterfly.left}%`,
            transform: `translate(-50%, -50%) scale(${butterfly.scale})`,
            transition: "top 2.5s ease, left 2.5s ease, transform 2.5s ease",
            transitionDelay: `${butterfly.delay}ms`,
          }}
        >
          <svg
            width="30"
            height="30"
            viewBox="0 0 100 100"
            fill={butterfly.color}
          >
            <path
              className="butterfly-wing"
              d="M50 50 C20 0, 0 30, 45 50 C0 70, 20 100, 50 50 C80 100, 100 70, 55 50 C100 30, 80 0, 50 50 Z"
            />
          </svg>
        </div>
      ))}
    </div>
  );
}
