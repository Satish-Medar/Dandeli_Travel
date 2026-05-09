# ✅ Responsive Design Checklist

Use this checklist to ensure all components and pages are fully responsive.

---

## 📱 Mobile Devices (320px - 640px)

### Layout
- [ ] No horizontal scrolling
- [ ] Single column layout
- [ ] Full-width images
- [ ] Stacked components
- [ ] Proper spacing between elements

### Navigation
- [ ] Hamburger menu for navigation
- [ ] Menu closes after selection
- [ ] Touch-friendly menu items (≥44px)
- [ ] No overlapping menu items
- [ ] Proper z-index layering

### Typography
- [ ] Text sizes readable (≥14px minimum)
- [ ] Proper line-height (≥1.5)
- [ ] No text overflow
- [ ] Headings sized appropriately
- [ ] Links are clickable (≥44px)

### Images
- [ ] Responsive images using Next.js `Image`
- [ ] Proper aspect ratios maintained
- [ ] No image distortion
- [ ] Images load quickly
- [ ] Alt text present

### Forms
- [ ] Input fields full-width
- [ ] Labels clear and readable
- [ ] Form fields ≥44px tall
- [ ] Touch keyboard appears correctly
- [ ] Submit button easy to tap

### Buttons
- [ ] Buttons ≥44x44px
- [ ] Clear visual hierarchy
- [ ] Proper spacing between buttons
- [ ] Click targets not too close
- [ ] Visible focus states

---

## 📱 Tablets (768px - 1024px)

### Layout
- [ ] Multi-column layout (2 columns)
- [ ] Proper content distribution
- [ ] Adequate white space
- [ ] No gaps in layout
- [ ] Scalable components

### Navigation
- [ ] Full navigation visible on larger tablets
- [ ] Mobile menu optional
- [ ] Menu items well-spaced
- [ ] Logo visible
- [ ] Action buttons visible

### Typography
- [ ] Font sizes scaled appropriately
- [ ] Line-height readable
- [ ] Headings prominent
- [ ] Body text comfortable to read
- [ ] Links properly sized

### Images
- [ ] Medium-sized images
- [ ] Aspect ratios correct
- [ ] Gallery layouts working
- [ ] Image optimization applied
- [ ] Smooth image loading

### Components
- [ ] Cards properly sized
- [ ] Grid layouts responsive
- [ ] Modals fit screen
- [ ] Dropdowns accessible
- [ ] Media players responsive

---

## 🖥️ Desktop (1024px+)

### Layout
- [ ] Multi-column layout (3+ columns)
- [ ] Full content width utilized
- [ ] Proper margins/padding
- [ ] Sidebar visible when applicable
- [ ] Optimal reading width (≤100 chars)

### Navigation
- [ ] Full navigation menu visible
- [ ] No mobile menu needed
- [ ] Hover effects visible
- [ ] Dropdowns working
- [ ] Breadcrumbs present if needed

### Typography
- [ ] Optimal font sizes
- [ ] Proper line-height
- [ ] Headings prominent
- [ ] Body text comfortable
- [ ] Multiple font sizes used

### Images
- [ ] Large, high-quality images
- [ ] Proper aspect ratios
- [ ] Carousels working
- [ ] Lightbox/modals functional
- [ ] Image optimization

### Interactive Elements
- [ ] Hover effects visible
- [ ] Tooltips working
- [ ] Dropdowns functional
- [ ] Smooth transitions
- [ ] No mobile-only UI

---

## 🎨 Visual Design

### Colors
- [ ] Colors consistent across breakpoints
- [ ] Text contrast ≥4.5:1
- [ ] Focus states visible
- [ ] Hover states clear
- [ ] Links underlined or styled

### Typography
- [ ] Font sizes scale smoothly
- [ ] Line heights appropriate
- [ ] Letter spacing readable
- [ ] Font weights used correctly
- [ ] No orphaned text

### Spacing
- [ ] Padding responsive
- [ ] Margins proportional
- [ ] Gaps between elements
- [ ] White space used effectively
- [ ] Consistency across pages

---

## ⚡ Performance

### Images
- [ ] Images optimized for size
- [ ] WebP/AVIF formats used
- [ ] Lazy loading implemented
- [ ] Responsive image sizes
- [ ] Priority images loaded first

### CSS
- [ ] CSS minified
- [ ] No unused styles
- [ ] Efficient selectors
- [ ] Media queries organized
- [ ] Responsive CSS file linked

### JavaScript
- [ ] Minimal JS for responsiveness
- [ ] Event listeners cleaned up
- [ ] No memory leaks
- [ ] Touch events optimized
- [ ] Debounced resize handlers

### Loading
- [ ] Page loads quickly on mobile
- [ ] Images load progressively
- [ ] Content visible quickly
- [ ] No layout shift
- [ ] Smooth interactions

---

## ♿ Accessibility

### Mobile
- [ ] Touch targets ≥44x44px
- [ ] Proper zoom enabled
- [ ] No text too small
- [ ] Color not only indicator
- [ ] Touch gestures have alternatives

### Semantic HTML
- [ ] Proper heading hierarchy
- [ ] Semantic elements used
- [ ] ARIA labels where needed
- [ ] Form labels present
- [ ] Skip links available

### Focus
- [ ] Focus visible on all elements
- [ ] Focus order logical
- [ ] No focus traps
- [ ] Keyboard navigation works
- [ ] Tab order correct

---

## 🧪 Testing Checklist

### Browser Testing
- [ ] Chrome/Edge latest
- [ ] Firefox latest
- [ ] Safari latest
- [ ] Mobile Chrome
- [ ] Mobile Safari

### Device Testing
- [ ] iPhone SE (375px)
- [ ] iPhone 12 Pro (390px)
- [ ] iPhone 14 Pro Max (430px)
- [ ] Galaxy S20 (360px)
- [ ] iPad (768px)
- [ ] iPad Pro (1024px)

### Orientation Testing
- [ ] Portrait mode looks good
- [ ] Landscape mode works
- [ ] No content cut off
- [ ] Orientation change smooth
- [ ] Layout adjusts correctly

### Network Testing
- [ ] Works on 4G
- [ ] Works on 3G
- [ ] Images load properly
- [ ] No timeouts
- [ ] Graceful degradation

### Touch Testing
- [ ] Touch events work
- [ ] Tap actions responsive
- [ ] Swipe gestures work
- [ ] Double-tap zoom works
- [ ] No unwanted selections

---

## 📋 Component Checklist

### Navigation Components
- [ ] Navbar responsive
- [ ] Menu toggles correctly
- [ ] Links clickable
- [ ] Logo visible
- [ ] Search bar works

### Image Components
- [ ] Images responsive
- [ ] Aspect ratios correct
- [ ] Alt text present
- [ ] Loading states
- [ ] Error states

### Form Components
- [ ] Inputs responsive
- [ ] Labels visible
- [ ] Validation works
- [ ] Error messages clear
- [ ] Success states

### Card Components
- [ ] Cards stack on mobile
- [ ] Images scale correctly
- [ ] Text readable
- [ ] Buttons accessible
- [ ] Hover states work

### Grid Components
- [ ] 3 columns on desktop
- [ ] 2 columns on tablet
- [ ] 1 column on mobile
- [ ] Gaps responsive
- [ ] Items scale evenly

### Modal Components
- [ ] Modal fit screen
- [ ] Close button visible
- [ ] Content readable
- [ ] No overflow
- [ ] Backdrop visible

---

## 🎯 Breakpoint Testing

### Mobile Breakpoints
- [ ] 320px (Extra small phones)
- [ ] 375px (Standard phones)
- [ ] 428px (Larger phones)
- [ ] 480px (Phone landscape)

### Tablet Breakpoints
- [ ] 640px (Small tablet)
- [ ] 768px (Standard tablet)
- [ ] 820px (Tablet landscape)
- [ ] 1024px (Large tablet)

### Desktop Breakpoints
- [ ] 1024px (Small desktop)
- [ ] 1280px (Standard desktop)
- [ ] 1536px (Large desktop)
- [ ] 1920px (Full HD)

---

## 🔄 Maintenance Checklist

### Code Review
- [ ] CSS follows mobile-first approach
- [ ] Uses CSS variables
- [ ] No hardcoded sizes
- [ ] Media queries organized
- [ ] Comments explain responsive logic

### Documentation
- [ ] Components documented
- [ ] Breakpoints documented
- [ ] Classes explained
- [ ] Examples provided
- [ ] Maintenance guide included

### Updates
- [ ] Breakpoints consistent across project
- [ ] Font sizes using variables
- [ ] New components follow pattern
- [ ] Tests updated
- [ ] Documentation updated

---

## 📊 Performance Metrics

### Desktop Target
- [ ] Lighthouse: ≥90 (Performance)
- [ ] Load time: <3s
- [ ] LCP: <2.5s
- [ ] FID: <100ms
- [ ] CLS: <0.1

### Mobile Target
- [ ] Lighthouse: ≥85 (Performance)
- [ ] Load time: <5s
- [ ] LCP: <3.5s
- [ ] FID: <100ms
- [ ] CLS: <0.1

---

## ✨ Final Verification

Before launching, verify:

- [ ] All breakpoints tested
- [ ] No horizontal scrolling on any device
- [ ] Images look good on all sizes
- [ ] Text readable everywhere
- [ ] Forms work on mobile
- [ ] Touch interactions smooth
- [ ] Performance acceptable
- [ ] Accessibility meets WCAG
- [ ] Cross-browser compatible
- [ ] Team sign-off obtained

---

**Project is ready for deployment when all checkboxes are checked! ✅**
