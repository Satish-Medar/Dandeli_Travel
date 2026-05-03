import Link from "next/link";
import Image from "next/image";

export const metadata = {
  title: "Explore Dandeli | Vana AI",
  description: "Discover the best activities and experiences in Dandeli, from River Rafting on the Kali River to Jungle Safaris.",
};

export default function ExplorePage() {
  return (
    <div className="content-page">
      <header className="page-hero">
        <div className="container">
          <h1>Explore <span className="text-accent">Dandeli</span></h1>
          <p className="lead">Discover the thrilling adventures and serene nature reserves that make Dandeli a premier destination.</p>
        </div>
      </header>

      <div className="container">
        <div className="explore-grid" style={{ marginBottom: '80px' }}>
          
          <div className="adventure-card">
            <Image src="/images/dandeli_rafting.png" alt="White Water Rafting" fill />
            <div className="adventure-overlay">
              <h3>White Water Rafting</h3>
              <p>The Kali River offers some of the best white water rafting in South India, with rapids ranging from Grade 2 to Grade 3.</p>
              <div className="explore-tags" style={{ marginTop: '16px' }}>
                <span className="tag">Adventure</span>
                <span className="tag">Water Sports</span>
              </div>
            </div>
          </div>

          <div className="adventure-card">
            <Image src="/images/dandeli_safari.png" alt="Jungle Safari" fill />
            <div className="adventure-overlay">
              <h3>Jungle Safari</h3>
              <p>Embark on an open-jeep safari through the Dandeli Wildlife Sanctuary. Spot black panthers, elephants, and deer in their natural habitat.</p>
              <div className="explore-tags" style={{ marginTop: '16px' }}>
                <span className="tag">Wildlife</span>
                <span className="tag">Family Friendly</span>
              </div>
            </div>
          </div>

          <div className="adventure-card">
            <Image src="/images/dandeli_bird.png" alt="Bird Watching" fill />
            <div className="adventure-overlay">
              <h3>Bird Watching</h3>
              <p>Home to over 200 species of birds, including the majestic Malabar Pied Hornbill. A true paradise for ornithologists and photographers.</p>
              <div className="explore-tags" style={{ marginTop: '16px' }}>
                <span className="tag">Nature</span>
                <span className="tag">Photography</span>
              </div>
            </div>
          </div>

          <div className="adventure-card">
            <Image src="/images/dandeli_trekking.png" alt="Forest Trekking" fill />
            <div className="adventure-overlay">
              <h3>Forest Trekking</h3>
              <p>Guided treks through the dense Western Ghats. Discover hidden waterfalls, limestone caves, and incredible panoramic viewpoints.</p>
              <div className="explore-tags" style={{ marginTop: '16px' }}>
                <span className="tag">Trekking</span>
                <span className="tag">Fitness</span>
              </div>
            </div>
          </div>

        </div>
        
        <div className="page-cta text-center mt-l">
          <h3>Want to build an itinerary around these activities?</h3>
          <p className="mb-m text-muted">Tell the AI what you want to do, and it will plan a custom trip for you.</p>
          <Link href="/chat" className="btn-primary large mx-auto">Ask the AI Planner</Link>
        </div>
      </div>
    </div>
  );
}
