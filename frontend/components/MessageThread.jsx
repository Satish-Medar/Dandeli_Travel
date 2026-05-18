/* Chat UI component displaying conversation threads. */
/* File: frontend/components/MessageThread.jsx */

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
      return (
        <div key={index} className="assistant-item">
          {formatInline(line.replace(/^([\-*])\s+/, ""))}
        </div>
      );
    }

    if (
      /^(Why it fits|Tradeoff|Location|Price|Estimated total|Rating|Description|Category|Website|Phone|Email|Unique Features):/.test(
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
      width="18"
      height="18"
      viewBox="0 0 24 24"
      fill="none"
      stroke="currentColor"
      strokeWidth="2"
      strokeLinecap="round"
      strokeLinejoin="round"
    >
      <path d="M12 2v20M17 5H9.5a3.5 3.5 0 0 0 0 7h5a3.5 3.5 0 0 1 0 7H6" />
    </svg>
  );

  return (
    <article className={`message-row ${message.role}`}>
      {message.role === "assistant" && (
        <div className="avatar assistant">{assistantIcon}</div>
      )}

      <div
        className={`message-card ${message.role} ${message.streaming ? "streaming" : ""}`}
      >
        <div className="message-body">
          {message.role === "assistant"
            ? renderAssistantBlock(message.content)
            : message.content}
        </div>
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
