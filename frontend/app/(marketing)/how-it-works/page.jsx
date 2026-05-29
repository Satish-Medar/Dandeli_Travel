/*
  Marketing page: How It Works

  Purpose:
  - Present a short, scannable explanation of how the chat-based travel
    assistant works for end users.
  - Break the page into clear scaffolded sections (hero, timeline, audience,
    call-to-action) so designers and developers can quickly find and update
    content.

  Annotation guidance:
  - Comments appear above each logical block (imports, metadata, component,
    and each major JSX section). They explain intent and where to change
    behavior or copy.
*/

/*
  Imports
  - `Link` from Next.js: client navigation helper for the CTA link.
  - `ScrollSection`, `ScrollGrid`: small layout/animation helpers used to
    stagger and animate blocks as the user scrolls. See
    `frontend/components/ScrollAnimation` for implementation details.
*/
import Link from "next/link";
import { ScrollSection, ScrollGrid } from "../../../components/ScrollAnimation";

/*
  Page metadata
  - Exported so Next.js can populate <head> title/description for SEO and
    social sharing. Change `title` or `description` to alter meta tags.
*/
export const metadata = {
  title: "How it Works | WayFind",
  description: "Learn how to use WayFind to plan your perfect getaway.",
};

/*
  Component: HowItWorksPage
  - Top-level React component that returns static JSX describing the
    assistant workflow. This file intentionally contains presentational
    content only — no state or data fetching — to keep the page immutable
    and cacheable.
*/
export default function HowItWorksPage() {
  return (
    <div className="content-page bg-muted">
      {/*
        Hero Section
        - Purpose: show a short tagline and headline that sets expectations.
        - `ScrollSection` wraps the block to apply entrance animations and
          spacing rules defined by the animation helper.
      */}
      <ScrollSection className="page-hero">
        <div className="container">
          {/* Small badge used as a visual hook above the headline */}
          <div className="badge mx-auto">Simple. Fast. Direct.</div>
          <h1>
            How to use the <span className="text-accent">Assistant</span>
          </h1>
          {/* Short lead paragraph describing the main benefit */}
          <p className="lead">
            Planning a trip to Dandeli has never been this effortless.
          </p>
        </div>
      </ScrollSection>

      {/*
        Timeline Section
        - Purpose: step-through explanation of the user flow in three clear
          cards. Each `timeline-item` contains a number, title and short
          description. Modify copy here to change messaging.
        - `ScrollGrid` provides staggered animations; `childDelay` controls
          the millisecond delay between each child's entrance.
      */}
      <ScrollSection className="container timeline-section">
        <div className="timeline">
          {/* Decorative vertical line for visual timeline */}
          <div className="timeline-line"></div>
          <ScrollGrid className="timeline-items" childDelay={140}>
            {/*
              Timeline item 1:
              - Explains how to start a conversational search. Keep examples
                concise; avoid long blocks of copy inside the JSX for
                maintainability (move to a localization/copy file if needed).
            */}
            <div className="timeline-item">
              <div className="timeline-number">1</div>
              <div className="timeline-content">
                <h3>Tell the AI what you want</h3>
                <p>
                  Forget rigid search filters. Just open the chat and talk
                  naturally. You can describe your budget, who you are traveling
                  with, and what activities you enjoy.
                </p>
                {/* Example bubble: short example user prompt */}
                <div className="example-bubble">
                  "I'm looking for a peaceful resort under 4000 INR for my
                  family. We want to do jungle safari and have a swimming pool."
                </div>
              </div>
            </div>

            {/*
              Timeline item 2:
              - Explains the assistant's comparison behavior. If the numeric
                claim ("70-Billion parameter AI") needs to change, update
                copy here rather than the code structure.
            */}
            <div className="timeline-item">
              <div className="timeline-number">2</div>
              <div className="timeline-content">
                <h3>Get Unbiased Comparisons</h3>
                <p>
                  Our 70-Billion parameter AI instantly scans hundreds of
                  verified local resorts. It doesn't push "sponsored" listings.
                  It simply analyzes the data and provides a customized, honest
                  comparison of the best options that fit your exact needs.
                </p>
              </div>
            </div>

            {/*
              Timeline item 3:
              - Explains booking flow and privacy-safety note (booking forwarded
                to resort WhatsApp). Keep technical details out of copy — if
                you need to link to an implementation note, add a comment.
            */}
            <div className="timeline-item">
              <div className="timeline-number">3</div>
              <div className="timeline-content">
                <h3>Book Directly via WhatsApp</h3>
                <p>
                  When you've found the perfect resort, just say{" "}
                  <strong>"Book it."</strong> The AI will ask for your dates and
                  contact info. Once you confirm, it securely forwards your
                  booking request directly to the resort owner's personal
                  WhatsApp.
                </p>
                <div className="example-bubble accent">
                  "Your booking request has been sent! The resort owner has been
                  notified on WhatsApp."
                </div>
              </div>
            </div>
          </ScrollGrid>
        </div>
      </ScrollSection>

      {/*
        Audience Section
        - Purpose: quick target-audience bullets so visitors self-identify.
        - Each `card` is a reusable presentational block; update titles or
          descriptions here to change audience messaging.
      */}
      <ScrollSection className="audience-section mt-l">
        <h2 className="text-center mb-m">Who is this for?</h2>
        <div className="grid-3">
          <div className="card">
            <h4>Families</h4>
            <p>
              Find safe, comfortable resorts with kid-friendly food and
              activities without spending hours reading confusing reviews.
            </p>
          </div>
          <div className="card">
            <h4>Adventure Seekers</h4>
            <p>
              Instantly locate the resorts that offer the best white-water river
              rafting packages on the Kali River.
            </p>
          </div>
          <div className="card">
            <h4>Nature Lovers</h4>
            <p>
              Discover secluded eco-camps deep inside the Dandeli Wildlife
              Sanctuary for the ultimate bird-watching experience.
            </p>
          </div>
        </div>
      </ScrollSection>

      {/*
        Call-to-action (CTA)
        - A single primary CTA that navigates users to the interactive chat.
        - Uses Next.js `Link` for client-side navigation. Replace the `href`
          if the route changes or is localized.
      */}
      <ScrollSection className="page-cta text-center mt-l">
        <Link href="/chat" className="btn-primary large mx-auto">
          Try it for yourself
        </Link>
      </ScrollSection>
    </div>
  );
}
