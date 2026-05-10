"use client";

import { useEffect } from "react";
import { useScrollAnimation } from "../lib/useScrollAnimation";

/**
 * ScrollTrigger - Auto-applies scroll animations to sections
 * Usage: Wrap your content or add data-scroll-animate to any element
 */
export function ScrollTrigger({
  children,
  className = "",
  animation = "fade-up",
}) {
  return <div className={className}>{children}</div>;
}

/**
 * Auto Scroll Animations - Disabled - showing all content immediately
 */
export function AutoScrollAnimations() {
  return null;
}

/**
 * Parallax Scroll Effect - Creates depth parallax effect on scroll
 */
export function ParallaxSection({ children, intensity = 0.5 }) {
  useEffect(() => {
    const handleScroll = () => {
      const elements = document.querySelectorAll("[data-parallax]");
      elements.forEach((el) => {
        const yOffset = window.pageYOffset;
        const elementOffset = el.offsetTop;
        const distanceFromTop = yOffset - elementOffset;
        const translateY = distanceFromTop * intensity;
        el.style.transform = `translateY(${translateY}px)`;
      });
    };

    window.addEventListener("scroll", handleScroll);
    return () => window.removeEventListener("scroll", handleScroll);
  }, [intensity]);

  return <div data-parallax>{children}</div>;
}

/**
 * Stagger List Items - Applies staggered animations to list children
 */
export function StaggerList({ children, delay = 100, animation = "fade-up" }) {
  const containerRef = useScrollAnimation({ triggerOnce: true });

  useEffect(() => {
    if (containerRef.current) {
      const items = containerRef.current.querySelectorAll("> *");
      items.forEach((item, index) => {
        item.style.animation = `${animation} 0.7s ease-out forwards`;
        item.style.animationDelay = `${index * delay}ms`;
      });
    }
  }, [delay, animation]);

  return <div ref={containerRef.current}>{children}</div>;
}
