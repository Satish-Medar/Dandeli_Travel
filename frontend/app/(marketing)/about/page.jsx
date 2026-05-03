import Link from "next/link";

export const metadata = {
  title: "About Us | Vana AI",
  description: "Learn how we're changing the way travelers explore Dandeli by connecting them directly with local resorts through AI.",
};

export default function AboutPage() {
  return (
    <div className="content-page">
      <header className="page-hero">
        <div className="container">
          <h1>Built for the Locals.<br/><span className="text-accent">Powered by AI.</span></h1>
          <p className="lead">We are on a mission to completely eliminate middle-man aggregators and bring tourism revenue back to the local families of Dandeli.</p>
        </div>
      </header>

      <div className="container">

        <article className="prose">
          <h2>The Problem</h2>
          <p>
            Dandeli is home to some of the most breathtaking nature reserves, wildlife sanctuaries, and river rafting experiences in India. However, the local resort owners—many of whom have lived here their entire lives—are forced to rely on massive online travel agencies (OTAs) to find guests.
          </p>
          <p>
            These aggregators charge exorbitant commission fees (often up to 30%), forcing resort owners to raise prices and stripping away their profit margins. Worse, travelers are presented with confusing, manipulative search results designed to push the most profitable listings rather than the best experiences.
          </p>

          <h2>Our Solution</h2>
          <p>
            We built <strong>Vana AI</strong> to change this. By leveraging state-of-the-art 70-billion parameter Artificial Intelligence, we created a system that understands exactly what you want—whether that's a quiet riverside retreat or an action-packed jungle adventure.
          </p>
          <p>
            When you decide to book, our system doesn't charge a fee. Instead, it securely generates a booking request and sends it <strong>directly to the resort owner's personal WhatsApp</strong>. 
          </p>
          
          <div className="stats-grid">
            <div className="stat-card">
              <h3>0%</h3>
              <p>Commission Fees</p>
            </div>
            <div className="stat-card">
              <h3>100%</h3>
              <p>Local Revenue</p>
            </div>
            <div className="stat-card">
              <h3>24/7</h3>
              <p>AI Availability</p>
            </div>
          </div>

          <h2>Why AI?</h2>
          <p>
            Traditional search filters (like clicking checkboxes for "Pool" or "Wifi") are rigid and frustrating. With our AI, you can just talk. You can say: <em>"Find me a resort that is great for kids, under 4000 rupees, and has bird watching."</em> The AI instantly reads through hundreds of verified local resort details and gives you the exact answer.
          </p>

          <div className="page-cta">
            <h3>Ready to support local tourism?</h3>
            <Link href="/chat" className="btn-primary">Start Planning</Link>
          </div>
        </article>
      </div>
    </div>
  );
}
