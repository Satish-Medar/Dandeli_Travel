import { useEffect, useRef, useState } from "react";

/**
 * Custom hook for scroll-triggered animations
 * Uses Intersection Observer API for performance
 */
export function useScrollAnimation(options = {}) {
  const {
    threshold = 0.1,
    rootMargin = "0px 0px -50px 0px",
    triggerOnce = false,
  } = options;

  const ref = useRef(null);
  const [isVisible, setIsVisible] = useState(false);
  const [hasTriggered, setHasTriggered] = useState(false);

  useEffect(() => {
    const observer = new IntersectionObserver(
      ([entry]) => {
        if (entry.isIntersecting) {
          setIsVisible(true);
          setHasTriggered(true);
          if (triggerOnce && ref.current) {
            observer.unobserve(ref.current);
          }
        } else if (!triggerOnce) {
          setIsVisible(false);
        }
      },
      {
        threshold: 0.2,
        rootMargin: "0px 0px -80px 0px",
      },
    );

    if (ref.current) {
      observer.observe(ref.current);
    }

    return () => {
      if (ref.current) {
        observer.unobserve(ref.current);
      }
    };
  }, [threshold, rootMargin, triggerOnce]);

  return { ref, isVisible: triggerOnce ? hasTriggered : isVisible };
}

/**
 * Stagger animation hook for multiple children
 */
export function useStaggerAnimation(childCount = 0, delay = 100) {
  const containerRef = useRef(null);
  const [visibleIndices, setVisibleIndices] = useState(new Set());
  const [hasStarted, setHasStarted] = useState(false);

  useEffect(() => {
    const observer = new IntersectionObserver(
      ([entry]) => {
        if (entry.isIntersecting && !hasStarted) {
          setHasStarted(true);
          // Stagger the animations
          for (let i = 0; i < childCount; i++) {
            setTimeout(() => {
              setVisibleIndices((prev) => new Set(prev).add(i));
            }, i * delay);
          }
          observer.unobserve(containerRef.current);
        }
      },
      {
        threshold: 0.2,
        rootMargin: "0px 0px -80px 0px",
      },
    );

    if (containerRef.current) {
      observer.observe(containerRef.current);
    }

    return () => {
      if (containerRef.current) {
        observer.unobserve(containerRef.current);
      }
    };
  }, [childCount, delay, hasStarted]);

  return { containerRef, visibleIndices };
}
