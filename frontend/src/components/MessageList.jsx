import React from "react";

function renderAssistantBlock(text) {
  const lines = text.split("\n");

  return lines.map((rawLine, index) => {
    const line = rawLine.trimEnd();
    if (!line.trim()) {
      return <div key={`gap-${index}`} className="assistant-gap" />;
    }

    if (/^[A-Z][A-Za-z\s'-]+:$/.test(line) || /^(Best match for your request|Backup option|One more option|Quick details|Closest alternatives if you want more options):?$/.test(line)) {
      return <div key={index} className="assistant-heading">{line}</div>;
    }

    if (/^\d+\.\s+/.test(line)) {
      return <div key={index} className="assistant-item">{line}</div>;
    }

    if (/^(Why it fits|Tradeoff|Location|Price|Estimated total|Rating|Description|Category|Website|Phone|Email|Unique Features):/.test(line)) {
      const [label, ...rest] = line.split(":");
      return (
        <div key={index} className="assistant-detail">
          <span className="assistant-label">{label}:</span>
          {rest.join(":")}
        </div>
      );
    }

    return <div key={index} className="assistant-paragraph">{line}</div>;
  });
}

function MessageBubble({ message }) {
  const avatarLabel = message.role === "assistant" ? "AI" : "You";
  const isMeta = message.role === "meta";

  return (
    <div className={`message-row ${message.role}`}>
      {!isMeta ? <div className={`avatar ${message.role}`}>{avatarLabel}</div> : null}
      <div className={`message ${message.role} ${message.streaming ? "streaming" : ""}`}>
        {message.role === "assistant" ? renderAssistantBlock(message.content) : message.content}
      </div>
    </div>
  );
}

export default function MessageList({ messages }) {
  return (
    <div className="chat-log">
      {messages.map((message) => (
        <MessageBubble key={message.id} message={message} />
      ))}
    </div>
  );
}
