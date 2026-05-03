"use client";

import { useEffect, useRef } from "react";

export default function Composer({
  value,
  onChange,
  onSubmit,
  onReset,
  pending,
  sessionTitle,
  clerkEnabled
}) {
  const textareaRef = useRef(null);

  useEffect(() => {
    const element = textareaRef.current;
    if (!element) {
      return;
    }
    element.style.height = "auto";
    element.style.height = `${Math.min(element.scrollHeight, 200)}px`;
  }, [value]);

  const handleKeyDown = (event) => {
    if (event.key === "Enter" && !event.shiftKey) {
      event.preventDefault();
      onSubmit();
    }
  };

  return (
    <form
      className="composer"
      onSubmit={(event) => {
        event.preventDefault();
        onSubmit();
      }}
    >
      <div className="composer-surface">
        <label className="composer-field" htmlFor="message-input">
          <textarea
            ref={textareaRef}
            id="message-input"
            name="message"
            rows="1"
            value={value}
            onChange={(event) => onChange(event.target.value)}
            placeholder="Message Vana..."
            onKeyDown={handleKeyDown}
          />
          <div className="composer-actions">
            <button 
              type="submit" 
              className="primary-button" 
              disabled={pending || !value.trim()}
              title="Send message"
            >
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round">
                <line x1="12" y1="19" x2="12" y2="5"></line>
                <polyline points="5 12 12 5 19 12"></polyline>
              </svg>
            </button>
          </div>
        </label>
        
        {/* We can hide title and use the hint since the overall layout changed */}
        <div className="composer-footer">
          <p className="composer-hint">
            Vana AI • Developed by Human.
          </p>
        </div>
      </div>
    </form>
  );
}
