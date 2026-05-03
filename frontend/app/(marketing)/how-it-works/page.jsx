import Link from "next/link";

export const metadata = {
  title: "How it Works | Vana AI",
  description: "Learn how to use Vana AI to plan your perfect getaway.",
};

export default function HowItWorksPage() {
  return (
    <div className="content-page bg-muted">
      <header className="page-hero">
        <div className="container">
          <div className="badge mx-auto">Simple. Fast. Direct.</div>
          <h1>How to use the <span className="text-accent">Assistant</span></h1>
          <p className="lead">Planning a trip to Dandeli has never been this effortless.</p>
        </div>
      </header>

      <div className="container">

        <div className="timeline">
          <div className="timeline-item">
            <div className="timeline-number">1</div>
            <div className="timeline-content">
              <h3>Tell the AI what you want</h3>
              <p>Forget rigid search filters. Just open the chat and talk naturally. You can describe your budget, who you are traveling with, and what activities you enjoy.</p>
              <div className="example-bubble">
                "I'm looking for a peaceful resort under 4000 INR for my family. We want to do jungle safari and have a swimming pool."
              </div>
            </div>
          </div>

          <div className="timeline-item">
            <div className="timeline-number">2</div>
            <div className="timeline-content">
              <h3>Get Unbiased Comparisons</h3>
              <p>Our 70-Billion parameter AI instantly scans hundreds of verified local resorts. It doesn't push "sponsored" listings. It simply analyzes the data and provides a customized, honest comparison of the best options that fit your exact needs.</p>
            </div>
          </div>

          <div className="timeline-item">
            <div className="timeline-number">3</div>
            <div className="timeline-content">
              <h3>Book Directly via WhatsApp</h3>
              <p>When you've found the perfect resort, just say <strong>"Book it."</strong> The AI will ask for your dates and contact info. Once you confirm, it securely forwards your booking request directly to the resort owner's personal WhatsApp.</p>
              <div className="example-bubble accent">
                "Your booking request has been sent! The resort owner has been notified on WhatsApp."
              </div>
            </div>
          </div>
        </div>

        <div className="audience-section mt-l">
          <h2 className="text-center mb-m">Who is this for?</h2>
          <div className="grid-3">
            <div className="card">
              <h4>Families</h4>
              <p>Find safe, comfortable resorts with kid-friendly food and activities without spending hours reading confusing reviews.</p>
            </div>
            <div className="card">
              <h4>Adventure Seekers</h4>
              <p>Instantly locate the resorts that offer the best white-water river rafting packages on the Kali River.</p>
            </div>
            <div className="card">
              <h4>Nature Lovers</h4>
              <p>Discover secluded eco-camps deep inside the Dandeli Wildlife Sanctuary for the ultimate bird-watching experience.</p>
            </div>
          </div>
        </div>
        
        <div className="page-cta text-center mt-l">
          <Link href="/chat" className="btn-primary large mx-auto">Try it for yourself</Link>
        </div>
      </div>
    </div>
  );
}
