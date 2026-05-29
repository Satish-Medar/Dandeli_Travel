/*
  MessageThread - renders a list of chat messages

  Simple notes:
  - `renderAssistantBlock` converts assistant text (plain with simple
    markdown-like markers) into small, styled pieces (headings, lists,
    details). This keeps the assistant output readable in the UI.
  - `MessageBubble` handles different roles: `assistant`, `user`, `meta`.
*/

/* Helper: parse and format assistant text into JSX blocks */
function renderAssistantBlock(text) {
  const lines = text.split("\n");

  const formatInline = (value) =>
    value.split(/(\*\*[^*]+\*\*|\*[^*]+\*)/g).map((part, i) => {
      if (part.startsWith("**") && part.endsWith("**")) {
        return <strong key={i}>{part.slice(2, -2)}</strong>;
      }
      if (part.startsWith("*") && part.endsWith("*") && part.length > 1) {
        return <em key={i}>{part.slice(1, -1)}</em>;
      }
      return part;
    });

  return lines.map((rawLine, index) => {
    const line = rawLine.trimEnd();
    if (!line.trim()) {
      return <div key={`gap-${index}`} className="assistant-gap" />;
    }

    const headingMatch = line.match(/^\*\*([^*]+):\*\*\s*(.*)$/);
    if (headingMatch) {
      const [, label, rest] = headingMatch;
      if (rest.trim()) {
        return (
          <div key={index} className="assistant-callout">
            <span className="assistant-callout-label">{label}:</span>
            <span>{formatInline(rest.trim())}</span>
          </div>
        );
      }
      return (
        <div key={index} className="assistant-heading">
          {label}
        </div>
      );
    }

    const resortTitleMatch = line.match(/^\*\*(\d+\.\s+[^*]+)\*\*$/);
    if (resortTitleMatch) {
      return (
        <div key={index} className="assistant-resort-title">
          {resortTitleMatch[1]}
        </div>
      );
    }

    if (
      /^[A-Z][A-Za-z\s'-]+:$/.test(line) ||
      /^(Best match for your request|Backup option|One more option|Quick details|Closest alternatives if you want more options):?$/.test(
        line,
      )
    ) {
      return (
        <div key={index} className="assistant-heading">
          {formatInline(line)}
        </div>
      );
    }

    if (
      /^\d+\.\s+/.test(line) ||
      line.startsWith("- ") ||
      line.startsWith("* ")
    ) {
      const item = line.replace(/^(\d+\.)\s+/, "").replace(/^([\-*])\s+/, "");
      const factMatch = item.match(/^\*\*([^*]+):\*\*\s*(.*)$/);
      if (factMatch) {
        return (
          <div key={index} className="assistant-fact">
            <span className="assistant-fact-label">{factMatch[1]}</span>
            <span>{formatInline(factMatch[2])}</span>
          </div>
        );
      }
      return (
        <div key={index} className="assistant-item">
          {formatInline(item)}
        </div>
      );
    }

    if (
      /^(Why it fits|Tradeoff|Location|Price|Estimated total|Rating|Description|Category|Website|Phone|Email|Unique Features|Best for|Rooms|Food|Activities|Amenities|Special offer|My Pick|Quick Verdict):/.test(
        line,
      )
    ) {
      const [label, ...rest] = line.split(":");
      return (
        <div key={index} className="assistant-detail">
          <span className="assistant-label">{label}:</span>
          {formatInline(rest.join(":"))}
        </div>
      );
    }

    return (
      <div key={index} style={{ marginBottom: "6px" }}>
        {formatInline(line)}
      </div>
    );
  });
}

function parseBookingDetails(text) {
  const bookingIdMatch = text.match(/Booking ID:\s*([^\n\r]+)/i);
  const resortMatch = text.match(/Resort:\s*([^\n\r]+)/i);
  const datesMatch = text.match(/Dates:\s*([^\n\r]+)/i);
  const guestsMatch = text.match(/Guests:\s*([^\n\r]+)/i);
  const statusMatch = text.match(/Twilio Status:\s*([^\n\r]+)/i);

  return {
    bookingId: bookingIdMatch ? bookingIdMatch[1].trim() : "BK-UNKNOWN",
    resort: resortMatch ? resortMatch[1].trim() : "Dandeli Resort",
    dates: datesMatch ? datesMatch[1].trim() : "Flexible Dates",
    guests: guestsMatch ? guestsMatch[1].trim() : "1",
    status: statusMatch ? statusMatch[1].trim() : "delivered",
  };
}

function BookingCard({ details }) {
  return (
    <div className="booking-card">
      <div className="booking-card-header">
        <div className="booking-card-title">
          <svg
            width="14"
            height="14"
            viewBox="0 0 24 24"
            fill="none"
            stroke="currentColor"
            strokeWidth="2.5"
            strokeLinecap="round"
            strokeLinejoin="round"
          >
            <path d="M22 11.08V12a10 10 0 1 1-5.93-9.14" />
            <polyline points="22 4 12 14.01 9 11.01" />
          </svg>
          Booking Confirmed
        </div>
        <span className="booking-pulse-dot" />
      </div>
      <div className="booking-card-body">
        <div className="booking-resort-name">{details.resort}</div>
        
        <div className="booking-details-grid">
          <div className="booking-detail-row">
            <svg
              width="16"
              height="16"
              viewBox="0 0 24 24"
              fill="none"
              stroke="currentColor"
              strokeWidth="2"
              strokeLinecap="round"
              strokeLinejoin="round"
            >
              <rect x="3" y="4" width="18" height="18" rx="2" ry="2" />
              <line x1="16" y1="2" x2="16" y2="6" />
              <line x1="8" y1="2" x2="8" y2="6" />
              <line x1="3" y1="10" x2="21" y2="10" />
            </svg>
            <div>
              <span>Dates: </span>
              <span className="booking-detail-value">{details.dates}</span>
            </div>
          </div>

          <div className="booking-detail-row">
            <svg
              width="16"
              height="16"
              viewBox="0 0 24 24"
              fill="none"
              stroke="currentColor"
              strokeWidth="2"
              strokeLinecap="round"
              strokeLinejoin="round"
            >
              <path d="M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2" />
              <circle cx="9" cy="7" r="4" />
              <path d="M23 21v-2a4 4 0 0 0-3-3.87" />
              <path d="M16 3.13a4 4 0 0 1 0 7.75" />
            </svg>
            <div>
              <span>Guests: </span>
              <span className="booking-detail-value">{details.guests}</span>
            </div>
          </div>
        </div>
      </div>
      <div className="booking-card-footer">
        <div className="booking-id-container">
          <span>Booking ID:</span>
          <span className="booking-id-chip">{details.bookingId}</span>
        </div>
        <span className="booking-whatsapp-badge">
          <svg
            width="12"
            height="12"
            viewBox="0 0 24 24"
            fill="none"
            stroke="currentColor"
            strokeWidth="2.5"
            strokeLinecap="round"
            strokeLinejoin="round"
            style={{ marginRight: "4px" }}
          >
            <path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z" />
          </svg>
          {details.status === "delivered" ? "Notified on WhatsApp" : `Status: ${details.status}`}
        </span>
      </div>
    </div>
  );
}

function MessageBubble({ message }) {
  const isMeta = message.role === "meta";

  if (isMeta) {
    return (
      <article className="message-row meta">
        <div className="message-card meta">{message.content}</div>
      </article>
    );
  }

  // AI Assistant Icon SVG (Minimalist Sparkle/Bot icon)
  const assistantIcon = (
    <svg
      width="16"
      height="16"
      viewBox="0 0 24 24"
      fill="none"
      stroke="currentColor"
      strokeWidth="2.5"
      strokeLinecap="round"
      strokeLinejoin="round"
    >
      <path d="M12 2v20M17 5H9.5a3.5 3.5 0 0 0 0 7h5a3.5 3.5 0 0 1 0 7H6" />
    </svg>
  );

  const isBooking = message.role === "assistant" &&
                    !message.streaming &&
                    message.content.includes("Your booking request has been sent") &&
                    message.content.includes("Booking ID:");

  const renderContent = () => {
    if (message.role === "user") {
      return message.content;
    }
    if (isBooking) {
      const details = parseBookingDetails(message.content);
      return <BookingCard details={details} />;
    }
    return renderAssistantBlock(message.content);
  };

  return (
    <article className={`message-row ${message.role}`}>
      {/* Show assistant avatar for assistant messages */}
      {message.role === "assistant" && (
        <div className="avatar assistant">{assistantIcon}</div>
      )}

      <div
        className={`message-card ${message.role} ${message.streaming ? "streaming" : ""}`}
      >
        <div className="message-body">{renderContent()}</div>
      </div>
    </article>
  );
}

export default function MessageThread({ messages }) {
  return (
    <div className="message-thread">
      {messages.map((message) => (
        <MessageBubble key={message.id} message={message} />
      ))}
    </div>
  );
}
