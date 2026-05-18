<!-- Guide for scroll animation implementation and behavior. -->
<!-- File: SCROLL_ANIMATIONS_GUIDE.md -->

# Scroll Animation System Guide

## Overview

This project now has a powerful scroll animation system that creates fresh, dynamic loading effects when users scroll through your website. Content appears smoothly with fade-in, slide-up, and scale animations.

## Features

- ✨ **Smooth Fade-In/Fade-Up Animations** - Content loads smoothly as you scroll
- 🎯 **Intersection Observer API** - High-performance, efficient animations
- 📱 **Mobile Optimized** - Respects `prefers-reduced-motion` for accessibility
- ⚡ **Lightweight** - No external animation libraries required
- 🎨 **Customizable** - Easy to adjust timing, delays, and animation types

## Components & Hooks Available

### 1. ScrollSection (Recommended for Marketing Pages)

Wraps a section and applies fade-up animation on scroll.

```jsx
import { ScrollSection } from "@/components/ScrollAnimation";

<ScrollSection className="my-section">
  <h2>This will fade in on scroll</h2>
</ScrollSection>;
```

**Props:**

- `className`: CSS classes to apply
- `animation`: Type of animation (default: "fade-up")
  - Options: `fade-up`, `fade-down`, `fade-left`, `fade-right`, `fade-scale`, `zoom`
- `delay`: Delay in milliseconds before animation starts

### 2. ScrollTrigger (Advanced)

Lower-level component for custom scroll animation triggers.

```jsx
import { ScrollTrigger } from "@/components/ScrollTrigger";

<ScrollTrigger animation="fade-up" className="custom-class">
  <div>Content here</div>
</ScrollTrigger>;
```

### 3. useScrollAnimation Hook

Use this hook in your own components for custom scroll detection.

```jsx
import { useScrollAnimation } from "@/lib/useScrollAnimation";

export function MyComponent() {
  const { ref, isVisible } = useScrollAnimation({
    threshold: 0.1,
    triggerOnce: true,
  });

  return <div ref={ref}>{isVisible && <p>This element is visible!</p>}</div>;
}
```

**Options:**

- `threshold`: How much of the element must be visible (0-1)
- `rootMargin`: Additional margin around viewport (CSS syntax)
- `triggerOnce`: If true, animation only plays once

### 4. useStaggerAnimation Hook

For animating multiple items with staggered delays.

```jsx
import { useStaggerAnimation } from "@/lib/useScrollAnimation";

export function ItemList({ items }) {
  const { containerRef, visibleIndices } = useStaggerAnimation(
    items.length,
    100, // 100ms delay between items
  );

  return (
    <div ref={containerRef}>
      {items.map((item, i) => (
        <div
          key={i}
          className={visibleIndices.has(i) ? "animate-fade-up" : "opacity-0"}
        >
          {item}
        </div>
      ))}
    </div>
  );
}
```

### 5. AutoScrollAnimations (Global)

Add to your layout for automatic animations on any element with `data-scroll-animate`.

```jsx
// In app/layout.jsx
import { AutoScrollAnimations } from "@/components/ScrollTrigger";

export default function RootLayout({ children }) {
  return (
    <html>
      <body>
        <AutoScrollAnimations />
        {children}
      </body>
    </html>
  );
}
```

Then mark elements in your content:

```jsx
<div data-scroll-animate="fade-up">Content fades up on scroll</div>
<div data-scroll-animate="fade-left" data-scroll-once="false">
  Repeats every time it enters viewport
</div>
```

## CSS Animation Classes

Available animation classes:

- `.animate-fade-in` - Simple fade-in
- `.animate-fade-up` - Fade-in with upward motion
- `.animate-fade-down` - Fade-in with downward motion
- `.animate-fade-left` - Fade-in from left
- `.animate-fade-right` - Fade-in from right
- `.animate-fade-scale` - Fade-in with scale effect
- `.animate-zoom` - Fade-in with zoom effect

## Usage Examples

### Example 1: Marketing Page Hero Section

```jsx
import { ScrollSection } from "@/components/ScrollAnimation";

export default function HomePage() {
  return (
    <ScrollSection className="hero-wrapper" animation="fade-up">
      <h1>Welcome to WayFind</h1>
      <p>Your AI travel assistant</p>
    </ScrollSection>
  );
}
```

### Example 2: Feature Grid with Stagger

```jsx
import { useStaggerAnimation } from "@/lib/useScrollAnimation";

export function FeatureGrid({ features }) {
  const { containerRef, visibleIndices } = useStaggerAnimation(
    features.length,
    150,
  );

  return (
    <div ref={containerRef} className="grid grid-cols-3 gap-4">
      {features.map((feature, i) => (
        <div
          key={i}
          className={`card ${visibleIndices.has(i) ? "animate-fade-up opacity-100" : "opacity-0"}`}
          style={{ transitionDelay: `${i * 150}ms` }}
        >
          {feature.title}
        </div>
      ))}
    </div>
  );
}
```

### Example 3: Timeline with Sequential Animation

```jsx
import { ScrollSection } from "@/components/ScrollAnimation";

export function Timeline() {
  return (
    <ScrollSection className="timeline-section">
      <div className="timeline-item">Item 1</div>
      <div className="timeline-item">Item 2</div>
      <div className="timeline-item">Item 3</div>
    </ScrollSection>
  );
}
```

## Animation Timing

Default timings configured in `globals.css`:

- **Fade In**: 0.6s
- **Fade Up/Down/Left/Right**: 0.7s
- **Scale/Zoom**: 0.6-0.8s

Stagger delays:

- Adventure cards: 0.15s between items
- Timeline items: 0.15s between items
- Feature cards: varies based on position

## Performance Tips

1. **Use `triggerOnce: true`** - Stops observing after animation plays
2. **Optimize with `will-change`** - Applied automatically
3. **Respect `prefers-reduced-motion`** - Already built-in
4. **Mobile Optimization** - Faster animations on smaller screens

## Accessibility

The animation system automatically:

- ✅ Respects `prefers-reduced-motion` CSS media query
- ✅ Uses efficient Intersection Observer API
- ✅ Maintains semantic HTML
- ✅ Works with keyboard navigation
- ✅ Doesn't interfere with focus management

Users who prefer reduced motion will not see animations, but content will still be visible.

## Current Implementation Status

### Pages with Scroll Animations:

- ✅ Home Page (`(marketing)/page.jsx`)
- ✅ About Page (`(marketing)/about/page.jsx`)
- ✅ How It Works (`(marketing)/how-it-works/page.jsx`)
- ✅ Explore Page (`(marketing)/explore/page.jsx`)

### Components Using Scroll Animations:

- ✅ Hero Section
- ✅ Adventure Cards Grid
- ✅ Timeline Section
- ✅ CTA Section

## Future Enhancements

To add scroll animations to more pages:

1. Import ScrollSection:

```jsx
import { ScrollSection } from "@/components/ScrollAnimation";
```

2. Wrap your section:

```jsx
<ScrollSection className="my-section">{/* Your content */}</ScrollSection>
```

3. That's it! The scroll animation is applied automatically.

## Customization

To adjust animation timing globally, edit `globals.css`:

```css
.animate-fade-up {
  animation: fadeInUp 0.7s ease-out forwards; /* Change 0.7s to desired duration */
}
```

## Browser Support

- ✅ Chrome 51+
- ✅ Firefox 55+
- ✅ Safari 12.1+
- ✅ Edge 16+
- ✅ Mobile browsers (iOS Safari, Chrome Android)

Uses Intersection Observer API with no polyfills needed for modern browsers.

## Troubleshooting

### Animations not appearing?

1. Ensure the component uses `"use client"` directive (for Client Components)
2. Check that elements have sufficient scroll distance to be triggered
3. Verify browser DevTools - check for animation classes being applied

### Animation too fast/slow?

Edit the duration in `globals.css` animation definitions.

### Animation interferes with other effects?

Check z-index and transform properties - scroll animations use `transform` property which creates new stacking context.

---

**Created:** May 2024
**Last Updated:** May 10, 2026
