import Link from "next/link";
import Image from "next/image";

export default function Footer() {
  return (
    <footer className="footer">
      <div className="footer-container">
        <div className="footer-brand">
          <div className="brand-logo">
            <Image src="/assets/vana-logo.svg" alt="Vana AI Logo" width={32} height={32} className="brand-icon" />
            <span>Vana AI</span>
          </div>
          <p className="footer-description">
            Experience Dandeli intelligently. The first AI-powered travel agent connecting you directly with authentic local resorts.
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
        <p>&copy; {new Date().getFullYear()} Vana AI. Built by humans. Powered by Vana.</p>
      </div>
    </footer>
  );
}
