# 🎨 Responsive Components Implementation Guide

This guide shows how to make individual components responsive in your project.

---

## 📱 Responsive Image Component

### Using Next.js Image Component

**Bad (Not Responsive):**

```jsx
<img src="/images/hero.png" alt="Hero" style={{ width: "100%" }} />
```

**Good (Fully Responsive):**

```jsx
import Image from "next/image";

export default function HeroImage() {
  return (
    <Image
      src="/images/hero.png"
      alt="Hero image"
      fill // Fills container
      priority // Loads immediately
      className="hero-bg"
      sizes="(max-width: 640px) 100vw, (max-width: 1024px) 100vw, 100vw"
    />
  );
}
```

### Image Container CSS

```css
.image-container {
  position: relative;
  width: 100%;
  max-width: 600px;
  aspect-ratio: 16/9; /* Maintains aspect ratio */
  overflow: hidden;
}

@media (max-width: 768px) {
  .image-container {
    max-width: 100%;
  }
}
```

---

## 🧭 Responsive Navigation

### Mobile Menu Toggle Pattern

```jsx
const [mobileMenuOpen, setMobileMenuOpen] = useState(false);

useEffect(() => {
  // Close menu on resize
  const handleResize = () => {
    if (window.innerWidth > 768) {
      setMobileMenuOpen(false);
    }
  };
  window.addEventListener("resize", handleResize);
  return () => window.removeEventListener("resize", handleResize);
}, []);

return (
  <nav className={`menu ${mobileMenuOpen ? "open" : ""}`}>
    {/* Menu items */}
  </nav>
);
```

### CSS for Mobile Menu

```css
@media (max-width: 768px) {
  .menu {
    position: fixed;
    top: 70px;
    left: 0;
    width: 100%;
    max-height: 0;
    overflow: hidden;
    transition: max-height 0.3s ease;
    background: white;
  }

  .menu.open {
    max-height: 400px; /* Adjust as needed */
  }
}
```

---

## 📝 Responsive Typography

### Font Size Scaling

```css
:root {
  --fs-base: 1rem;
  --fs-lg: 1.25rem;
  --fs-xl: 1.5rem;
  --fs-2xl: 2rem;
  --fs-3xl: 2.5rem;
}

@media (max-width: 640px) {
  :root {
    --fs-base: 0.95rem;
    --fs-lg: 1.1rem;
    --fs-xl: 1.25rem;
    --fs-2xl: 1.5rem;
    --fs-3xl: 1.875rem;
  }
}

.heading {
  font-size: var(--fs-3xl);
  line-height: 1.2;
  margin-bottom: 1rem;
}

@media (max-width: 768px) {
  .heading {
    margin-bottom: 0.75rem;
  }
}
```

---

## 📐 Responsive Grid & Flex Layouts

### 3-Column Grid (Responsive)

```jsx
export default function ResortGrid({ resorts }) {
  return (
    <div className="resort-grid">
      {resorts.map((resort) => (
        <ResortCard key={resort.id} resort={resort} />
      ))}
    </div>
  );
}
```

```css
.resort-grid {
  display: grid;
  gap: 24px;
  grid-template-columns: repeat(3, 1fr);
}

@media (max-width: 1024px) {
  .resort-grid {
    grid-template-columns: repeat(2, 1fr);
  }
}

@media (max-width: 768px) {
  .resort-grid {
    grid-template-columns: 1fr;
    gap: 20px;
  }
}

@media (max-width: 640px) {
  .resort-grid {
    gap: 16px;
  }
}
```

---

## 🎯 Responsive Cards

### Card Component

```jsx
export default function ResortCard({ resort }) {
  return (
    <article className="resort-card">
      <div className="card-image">
        <Image
          src={resort.image}
          alt={resort.name}
          fill
          sizes="(max-width: 640px) 100vw, (max-width: 1024px) 50vw, 33vw"
        />
      </div>
      <div className="card-content">
        <h3>{resort.name}</h3>
        <p>{resort.description}</p>
        <button className="card-action">Learn More</button>
      </div>
    </article>
  );
}
```

```css
.resort-card {
  border-radius: 16px;
  overflow: hidden;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
  transition:
    transform 0.3s ease,
    box-shadow 0.3s ease;
  display: flex;
  flex-direction: column;
  height: 100%;
}

.resort-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.15);
}

@media (max-width: 768px) {
  .resort-card:hover {
    transform: none; /* Disable hover effect on touch devices */
  }
}

.card-image {
  position: relative;
  width: 100%;
  aspect-ratio: 16/9;
  overflow: hidden;
  background: #f0f0f0;
}

.card-content {
  padding: 24px;
  flex: 1;
  display: flex;
  flex-direction: column;
}

@media (max-width: 640px) {
  .card-content {
    padding: 16px;
  }
}

.card-content h3 {
  margin: 0 0 12px 0;
  font-size: var(--fs-lg);
  line-height: 1.3;
}

@media (max-width: 640px) {
  .card-content h3 {
    font-size: var(--fs-base);
  }
}

.card-action {
  margin-top: auto;
  padding: 10px 16px;
  border: none;
  border-radius: 8px;
  background: var(--accent);
  color: white;
  font-weight: 600;
  cursor: pointer;
  font-size: var(--fs-sm);
  transition: background 0.2s;
}

.card-action:hover {
  background: var(--accent-hover);
}
```

---

## 📱 Mobile-Optimized Forms

```jsx
export default function BookingForm() {
  const [formData, setFormData] = useState({
    dates: "",
    guests: "",
    budget: "",
  });

  return (
    <form className="booking-form">
      <input
        type="date"
        value={formData.dates}
        onChange={(e) => setFormData({ ...formData, dates: e.target.value })}
        placeholder="Select dates"
      />
      <select
        value={formData.guests}
        onChange={(e) => setFormData({ ...formData, guests: e.target.value })}
      >
        <option>Number of guests</option>
      </select>
      <button type="submit">Search Resorts</button>
    </form>
  );
}
```

```css
.booking-form {
  display: grid;
  gap: 16px;
  grid-template-columns: repeat(3, 1fr);
}

@media (max-width: 1024px) {
  .booking-form {
    grid-template-columns: repeat(2, 1fr);
  }
}

@media (max-width: 768px) {
  .booking-form {
    grid-template-columns: 1fr;
    gap: 12px;
  }
}

.booking-form input,
.booking-form select {
  padding: 12px;
  border: 1px solid #ddd;
  border-radius: 8px;
  font-size: var(--fs-base);
  font-family: inherit;
}

@media (max-width: 640px) {
  .booking-form input,
  .booking-form select {
    padding: 10px;
    font-size: var(--fs-sm);
  }
}

.booking-form button {
  padding: 12px 24px;
  grid-column: 1 / -1;
  background: var(--accent);
  color: white;
  border: none;
  border-radius: 8px;
  font-size: var(--fs-base);
  font-weight: 600;
  cursor: pointer;
  transition: background 0.2s;
}

@media (max-width: 640px) {
  .booking-form button {
    padding: 10px 20px;
    font-size: var(--fs-sm);
  }
}

.booking-form button:hover {
  background: var(--accent-hover);
}
```

---

## 🎨 Responsive Typography Styles

```jsx
// Use typography helper classes
<h1 className="heading-1">Page Title</h1>
<h2 className="heading-2">Section Title</h2>
<p className="body-text">Regular text</p>
<small className="caption">Small caption text</small>
```

```css
.heading-1 {
  font-size: var(--fs-4xl);
  font-weight: 800;
  line-height: 1.1;
  margin: 0 0 24px 0;
}

@media (max-width: 768px) {
  .heading-1 {
    font-size: var(--fs-3xl);
    margin-bottom: 16px;
  }
}

@media (max-width: 640px) {
  .heading-1 {
    font-size: var(--fs-2xl);
    margin-bottom: 12px;
  }
}

.heading-2 {
  font-size: var(--fs-3xl);
  font-weight: 700;
  line-height: 1.2;
  margin: 0 0 16px 0;
}

@media (max-width: 768px) {
  .heading-2 {
    font-size: var(--fs-2xl);
  }
}

@media (max-width: 640px) {
  .heading-2 {
    font-size: var(--fs-xl);
  }
}

.body-text {
  font-size: var(--fs-base);
  line-height: 1.6;
  color: var(--text-main);
}

.caption {
  font-size: var(--fs-xs);
  color: var(--text-muted);
  line-height: 1.4;
}
```

---

## 🧪 Testing Responsive Components

### Test Cases for Resorts Grid

```
✅ Mobile (320px):
   - Single column layout
   - Images display correctly
   - Text readable
   - Buttons easy to tap

✅ Tablet (768px):
   - Two-column layout
   - Balanced spacing
   - Cards properly sized
   - Touch interactions work

✅ Desktop (1024px):
   - Three-column layout
   - Full featured
   - Hover effects visible
   - Optimal spacing
```

---

## 💡 Common Patterns

### 1. Responsive Padding

```css
.container {
  padding: 48px 24px; /* Desktop */
}

@media (max-width: 768px) {
  .container {
    padding: 36px 20px; /* Tablet */
  }
}

@media (max-width: 640px) {
  .container {
    padding: 24px 16px; /* Mobile */
  }
}
```

### 2. Responsive Gap

```css
.grid {
  display: grid;
  gap: 32px; /* Desktop */
}

@media (max-width: 768px) {
  .grid {
    gap: 24px; /* Tablet */
  }
}

@media (max-width: 640px) {
  .grid {
    gap: 16px; /* Mobile */
  }
}
```

### 3. Responsive Flex Direction

```css
.row {
  display: flex;
  gap: 20px;
  flex-direction: row;
}

@media (max-width: 768px) {
  .row {
    flex-direction: column;
  }
}
```

---

## ✨ Best Practices Summary

1. **Mobile First**: Style for mobile, enhance for larger screens
2. **Use Variables**: Use CSS variables for consistent sizing
3. **Semantic HTML**: Use proper semantic elements
4. **Flexible Images**: Always use responsive images
5. **Touch Friendly**: Minimum 44px touch targets
6. **Test Thoroughly**: Test on real devices
7. **Performance**: Optimize images for different sizes
8. **Accessibility**: Maintain readable text sizes
9. **Consistency**: Use consistent breakpoints
10. **Maintenance**: Document responsive decisions

---

Your project is now ready for responsive development! 🚀
