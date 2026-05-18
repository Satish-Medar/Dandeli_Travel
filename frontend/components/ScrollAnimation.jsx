/* Component for applying scroll-based animations on page sections. */
/* File: frontend/components/ScrollAnimation.jsx */


"use client";

import { useState, useEffect } from "react";
import {
  useScrollAnimation,
  useStaggerAnimation,
} from "../lib/useScrollAnimation";
import {
  HeroSkeleton,
  CardSkeleton,
  SectionHeaderSkeleton,
  TextSkeleton,
} from "./Skeletons";

/**
 * ScrollSection - Wraps sections with fade-in & slide-up animations
 * Now supports skeleton loading
 */
export function ScrollSection({
  children,
  className = "",
  animation = "fade-up",
  delay = 0,
  skeletonType,
  skeletonDelay = 800,
}) {
  const { ref, isVisible } = useScrollAnimation({ triggerOnce: true });
  const [showSkeleton, setShowSkeleton] = useState(false);
  const [showContent, setShowContent] = useState(true);

  useEffect(() => {
    // Removed skeleton loading delay - show content immediately
    setShowSkeleton(false);
    setShowContent(true);
  }, []);

  const renderSkeleton = () => {
    switch (skeletonType) {
      case "hero":
        return <HeroSkeleton />;
      case "section-header":
        return <SectionHeaderSkeleton />;
      case "text":
        return <TextSkeleton />;
      default:
        return null;
    }
  };

  const animationClass = ""; // Removed animation effect

  return (
    <div ref={ref} className={`${className}`} style={{}}>
      {showContent && children}
    </div>
  );
}

/**
 * ScrollGrid - For grid items with staggered animations
 * Now supports skeleton loading for each item
 */
export function ScrollGrid({
  children,
  className = "",
  childDelay = 100,
  style,
  skeletonType,
  skeletonDelay = 600,
}) {
  const childArray = Array.isArray(children) ? children : [children];

  return (
    <div className={className} style={style}>
      {childArray.map((child, index) => {
        return (
          <div key={index} style={{}}>
            {child}
          </div>
        );
      })}
    </div>
  );
}

/**
 * ScrollItem - For individual items with fade-in animation
 */
export function ScrollItem({ children, className = "", delay = 0 }) {
  return <div className={className}>{children}</div>;
}