/* UI component rendering ambient bee animation effects. */
/* File: frontend/components/Wildlife/AmbientBees.jsx */


"use client";

import { useEffect, useState } from "react";

const randomPercent = () =>
  Math.max(5, Math.min(95, Math.floor(Math.random() * 90) + 5));
const randomScale = () => Number((0.7 + Math.random() * 0.6).toFixed(2));
const randomDelay = () => `${Math.random() * 1.5}s`;
const randomRotation = () => Math.floor(Math.random() * 360);

// Calculate angle between two points
const calculateAngle = (x1, y1, x2, y2) => {
  return Math.atan2(y2 - y1, x2 - x1) * (180 / Math.PI);
};

// Generate a new position that's not too far from current position
const generateNearbyPosition = (currentTop, currentLeft) => {
  const maxDistance = 30; // Maximum distance to move in percentage
  const angle = Math.random() * 2 * Math.PI; // Random direction
  const distance = Math.random() * maxDistance;

  const newTop = Math.max(
    5,
    Math.min(95, currentTop + Math.sin(angle) * distance),
  );
  const newLeft = Math.max(
    5,
    Math.min(95, currentLeft + Math.cos(angle) * distance),
  );

  return { top: newTop, left: newLeft };
};

const generateBee = (id) => ({
  id,
  top: randomPercent(),
  left: randomPercent(),
  delay: randomDelay(),
  scale: randomScale(),
  rotation: randomRotation(),
});

const generateBees = () => [1, 2, 3, 4, 5].map(generateBee);

export default function AmbientBees() {
  const [bees, setBees] = useState([]);

  useEffect(() => {
    setBees(generateBees());

    const interval = window.setInterval(() => {
      setBees((current) =>
        current.map((bee) => {
          const newPosition = generateNearbyPosition(bee.top, bee.left);
          const angle = calculateAngle(
            bee.left,
            bee.top,
            newPosition.left,
            newPosition.top,
          );

          return {
            ...bee,
            top: newPosition.top,
            left: newPosition.left,
            rotation: angle,
            scale: randomScale(),
            delay: randomDelay(),
          };
        }),
      );
    }, 6000); // Slower movement - every 6 seconds

    return () => window.clearInterval(interval);
  }, []);

  return (
    <div
      style={{
        position: "absolute",
        top: 0,
        left: 0,
        width: "100%",
        height: "100%",
        pointerEvents: "none",
        zIndex: 10,
      }}
    >
      {bees.map((bee) => (
        <div
          key={bee.id}
          className="ambient-bee"
          style={{
            position: "absolute",
            top: `${bee.top}%`,
            left: `${bee.left}%`,
            animationDelay: bee.delay,
            transform: `scale(${bee.scale}) rotate(${bee.rotation}deg)`,
            transition:
              "top 5s ease-in-out, left 5s ease-in-out, transform 2s ease-in-out",
          }}
        >
          <svg width="24" height="24" viewBox="0 0 100 100">
            <ellipse
              cx="50"
              cy="60"
              rx="15"
              ry="25"
              fill="#f59e0b"
              transform="rotate(45 50 60)"
            />
            <path
              d="M40 45 L65 70"
              stroke="#1f2937"
              strokeWidth="6"
              strokeLinecap="round"
            />
            <path
              d="M30 55 L55 80"
              stroke="#1f2937"
              strokeWidth="6"
              strokeLinecap="round"
            />
            <path
              className="bee-wing-l"
              d="M40 50 C20 10, 50 10, 45 45 Z"
              fill="#9ca3af"
              opacity="0.6"
            />
            <path
              className="bee-wing-r"
              d="M60 70 C90 90, 90 60, 55 65 Z"
              fill="#9ca3af"
              opacity="0.6"
            />
          </svg>
        </div>
      ))}
    </div>
  );
}