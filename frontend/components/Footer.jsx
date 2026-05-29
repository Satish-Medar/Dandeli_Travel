/*
  Footer component for the frontend site.

  Simple overview:
  - Displays brand information and quick navigation links.
  - Uses Next.js `Link` for internal page navigation.
*/
/* File: frontend/components/Footer.jsx */

import Link from "next/link";

export default function Footer() {
  return (
    <footer className="footer">
      <div className="footer-container">
        <div className="footer-brand">
          <div className="brand-logo">
            <div className="brand-logo-icon-wrapper">
              <img
                src="/assets/Gemini_Generated_Image.png"
                alt="WayFind Logo"
                className="brand-icon"
                width={60}
                height={60}
              />
            </div>
            <span>WayFind</span>
          </div>
          <p className="footer-description">
            Experience travel intelligently. The first AI-powered travel agent
            connecting you directly with authentic local resorts.
          </p>
        </div>
        <div className="footer-links">
          <div className="link-column">
            <h4>Explore</h4>
            <Link href="/explore">River Rafting</Link>
            <Link href="/explore">Jungle Safari</Link>
            <Link href="/explore">Bird Watching</Link>
          </div>
          <div className="link-column">
            <h4>Company</h4>
            <Link href="/about">About Us</Link>
            <Link href="/how-it-works">How it Works</Link>
            <Link href="/chat">Launch AI</Link>
          </div>
        </div>
      </div>
      <div className="footer-bottom">
        <p>
          &copy; {new Date().getFullYear()} WayFind. Built by humans. Powered by
          AI.
        </p>
      </div>
    </footer>
  );
}
