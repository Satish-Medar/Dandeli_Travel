import Link from "next/link";
import Image from "next/image";
import Butterflies from "../../components/Wildlife/Butterflies";
import AmbientBees from "../../components/Wildlife/AmbientBees";
import TigerGuide from "../../components/Wildlife/TigerGuide";
import TiltCard from "../../components/Wildlife/TiltCard";

export const metadata = {
  title: "Vana AI | Resort & Booking Assistant",
  description: "Experience Dandeli intelligently. The first AI-powered travel agent connecting you directly with authentic local resorts.",
};

export default function HomePage() {
  return (
    <>
      <Butterflies />
      <AmbientBees />
      <section className="hero-wrapper">
        <Image 
          src="/images/dandeli_hero.png" 
          alt="Dandeli Kali River" 
          fill
          priority
          className="hero-bg"
        />
        <div className="hero-overlay"></div>
        <div className="hero-section">
          <div className="hero-content">
            <div className="badge">Next Generation Travel</div>
            <h1 className="hero-title">
              Experience Dandeli.<br/>
              <span className="text-accent">Intelligently.</span>
            </h1>
            <p className="hero-subtitle">
              The world's first AI travel agent that connects you directly with authentic Dandeli eco-resorts. Plan river rafting, jungle safaris, and book directly via WhatsApp. No middlemen. No hidden fees.
            </p>
            <div className="hero-actions">
              <Link href="/chat" className="btn-primary large">
                Start Planning Free
              </Link>
              <Link href="/how-it-works" className="btn-secondary large">
                How it works
              </Link>
            </div>
          </div>
          
          <div className="glass-card">
            <div className="chat-bubble user">Find me a peaceful riverside eco-resort under 5000 INR with rafting.</div>
            <div className="chat-bubble ai">
              I found 2 perfect options: Bison River Resort and Kali River Retreat. Both offer direct river access and white-water rafting packages. Shall I place a booking request directly with the owners?
            </div>
          </div>
        </div>
      </section>

      <section className="adventure-section">
        <div className="wave-divider">
          <svg data-name="Layer 1" xmlns="http://www.w3.org/20event/svg" viewBox="0 0 1200 120" preserveAspectRatio="none">
            <path d="M321.39,56.44c58-10.79,114.16-30.13,172-41.86,82.39-16.72,168.19-17.73,250.45-.39C823.78,31,906.67,72,985.66,92.83c70.05,18.48,146.53,26.09,214.34,3V0H0V27.35A600.21,600.21,0,0,0,321.39,56.44Z" className="shape-fill"></path>
          </svg>
        </div>
        <div className="container">
          <div className="section-header">
            <h2>Discover the wild beauty of Dandeli</h2>
            <p>From roaring rivers to deep jungles, our AI finds the perfect experiences tailored precisely to your preferences.</p>
          </div>
          
          <div className="adventure-grid">
            <TiltCard>
              <div className="adventure-card">
                <Image src="/images/dandeli_rafting.png" alt="White Water Rafting" fill />
                <div className="adventure-overlay">
                  <h3>White Water Rafting</h3>
                  <p>Conquer the roaring rapids of the Kali River with expert guides. Perfect for thrill-seekers.</p>
                </div>
              </div>
            </TiltCard>
            <TiltCard>
              <div className="adventure-card">
                <Image src="/images/dandeli_safari.png" alt="Jungle Safari" fill />
                <div className="adventure-overlay">
                  <h3>Jungle Safari</h3>
                  <p>Spot black panthers, hornbills, and deer in the lush Dandeli Wildlife Sanctuary.</p>
                </div>
              </div>
            </TiltCard>
            <TiltCard>
              <div className="adventure-card">
                <Image src="/images/dandeli_resort.png" alt="Eco Resorts" fill />
                <div className="adventure-overlay">
                  <h3>Premium Eco-Resorts</h3>
                  <p>Stay in luxurious wooden cabins nestled deep in the forest with direct river access.</p>
                </div>
              </div>
            </TiltCard>
          </div>
        </div>
      </section>
      
      <section className="timeline-section">
        <div className="section-header">
          <h2>Travel planning, reimagined.</h2>
          <p>We replaced frustrating search aggregators with a brilliant AI agent.</p>
        </div>
        
        <TigerGuide />
        
        <div className="timeline-container">
          <div className="timeline-line"></div>
          
          <div className="timeline-item">
            <div className="timeline-dot"></div>
            <div className="timeline-content">
              <h3>1. Semantic Search</h3>
              <p>Just talk naturally. Our 70B parameter AI understands complex constraints like "family friendly with bird watching and vegetarian food" instantly.</p>
            </div>
          </div>
          
          <div className="timeline-item">
            <div className="timeline-dot"></div>
            <div className="timeline-content">
              <h3>2. Instant Itineraries</h3>
              <p>The AI dynamically generates customized day-by-day itineraries based on the specific resort you choose and your personal interests.</p>
            </div>
          </div>
          
          <div className="timeline-item">
            <div className="timeline-dot"></div>
            <div className="timeline-content">
              <h3>3. Direct WhatsApp Booking</h3>
              <p>When you're ready to book, the AI securely forwards your request directly to the resort owner's WhatsApp. No platform fees.</p>
            </div>
          </div>
        </div>
      </section>
      
      <section className="cta-section">
        <div className="cta-overlay-art"></div>
        <div className="cta-container">
          <h2>Ready to explore Dandeli?</h2>
          <p>Join thousands of travelers who have revolutionized their trip planning.</p>
          <Link href="/chat" className="btn-primary large mt-4">
            Start Your Journey
          </Link>
        </div>
      </section>
    </>
  );
}
