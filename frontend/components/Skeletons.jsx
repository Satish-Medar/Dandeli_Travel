"use client";

import { useState, useEffect } from "react";

/**
 * Skeleton Components for Loading States
 */

// Hero Section Skeleton
export function HeroSkeleton() {
  return (
    <div className="hero-section">
      <div className="hero-content">
        <div className="skeleton-badge"></div>
        <div className="skeleton-title"></div>
        <div className="skeleton-subtitle"></div>
        <div className="skeleton-actions">
          <div className="skeleton-button"></div>
          <div className="skeleton-button secondary"></div>
        </div>
      </div>
      <div className="glass-card">
        <div className="skeleton-chat-bubble user"></div>
        <div className="skeleton-chat-bubble ai"></div>
        <div className="skeleton-chat-bubble user"></div>
      </div>
    </div>
  );
}

// Card Skeleton
export function CardSkeleton({ type = "default" }) {
  if (type === "adventure") {
    return (
      <div className="adventure-card skeleton">
        <div className="skeleton-image"></div>
        <div className="adventure-overlay">
          <div className="skeleton-text short"></div>
          <div className="skeleton-text long"></div>
        </div>
      </div>
    );
  }

  if (type === "explore") {
    return (
      <div className="explore-card skeleton">
        <div className="skeleton-image explore"></div>
        <div className="explore-content">
          <div className="skeleton-text medium"></div>
          <div className="skeleton-text long"></div>
          <div className="skeleton-tags">
            <div className="skeleton-tag"></div>
            <div className="skeleton-tag"></div>
          </div>
        </div>
      </div>
    );
  }

  if (type === "stat") {
    return (
      <div className="stat-card skeleton">
        <div className="skeleton-stat-number"></div>
        <div className="skeleton-text short"></div>
      </div>
    );
  }

  return (
    <div className="card skeleton">
      <div className="skeleton-text medium"></div>
      <div className="skeleton-text long"></div>
      <div className="skeleton-text long"></div>
    </div>
  );
}

// Timeline Item Skeleton
export function TimelineSkeleton() {
  return (
    <div className="timeline-item skeleton">
      <div className="timeline-content">
        <div className="skeleton-text medium"></div>
        <div className="skeleton-text long"></div>
        <div className="skeleton-text long"></div>
      </div>
      <div className="timeline-dot"></div>
      <div className="timeline-content">
        <div className="skeleton-text medium"></div>
        <div className="skeleton-text long"></div>
      </div>
    </div>
  );
}

// Section Header Skeleton
export function SectionHeaderSkeleton() {
  return (
    <div className="section-header skeleton">
      <div className="skeleton-title"></div>
      <div className="skeleton-subtitle"></div>
    </div>
  );
}

// Text Content Skeleton
export function TextSkeleton({ lines = 3 }) {
  return (
    <div className="text-skeleton">
      {Array.from({ length: lines }, (_, i) => (
        <div
          key={i}
          className={`skeleton-text ${i === lines - 1 ? "short" : "long"}`}
        ></div>
      ))}
    </div>
  );
}

// Generic Skeleton Wrapper with Loading State
export function SkeletonWrapper({
  children,
  loading = true,
  skeleton: SkeletonComponent,
  delay = 1000,
  className = "",
}) {
  const [showSkeleton, setShowSkeleton] = useState(true);
  const [showContent, setShowContent] = useState(false);

  useEffect(() => {
    if (!loading) {
      // Show skeleton for minimum delay, then transition to content
      const timer = setTimeout(() => {
        setShowSkeleton(false);
        setTimeout(() => setShowContent(true), 150); // Small delay for smooth transition
      }, delay);

      return () => clearTimeout(timer);
    } else {
      setShowSkeleton(true);
      setShowContent(false);
    }
  }, [loading, delay]);

  return (
    <div className={`skeleton-wrapper ${className}`}>
      {showSkeleton && SkeletonComponent && <SkeletonComponent />}
      {showContent && children}
    </div>
  );
}
