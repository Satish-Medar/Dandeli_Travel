/*
  Composer - Chat input component

  Simple notes in plain language:
  - Props:
    - `value`: current textarea text
    - `onChange(text)`: called when user types
    - `onSubmit()`: called to send the message
    - `pending`: when true, disables the send button
  - Behavior:
    - Auto-resizes the textarea to fit content (max ~200px)
    - Press Enter (without Shift) to send
    - The send button is disabled when there's no text or while pending
*/

"use client";

import { useEffect, useRef } from "react";
import { SignInButton, SignUpButton } from "@clerk/nextjs";

export default function Composer({
  value,
  onChange,
  onSubmit,
  onReset,
  pending,
  sessionTitle,
  clerkEnabled,
  isLimitReached,
}) {
  // A ref to directly measure and resize the textarea element
  const textareaRef = useRef(null);

  // Auto-resize the textarea when `value` changes so it grows with content
  useEffect(() => {
    const element = textareaRef.current;
    if (!element) {
      return;
    }
    element.style.height = "auto"; // reset before measuring
    element.style.height = `${Math.min(element.scrollHeight, 200)}px`;
  }, [value]);

  if (isLimitReached) {
    return (
      <div className="composer-surface limit-reached-card" style={{
        padding: "24px 20px",
        borderRadius: "12px",
        border: "1px solid var(--ops-border)",
        background: "#ffffff",
        boxShadow: "var(--ops-shadow-sm)",
        textAlign: "center",
        display: "flex",
        flexDirection: "column",
        alignItems: "center",
        gap: "12px",
        maxWidth: "600px",
        margin: "0 auto 16px"
      }}>
        <div style={{
          width: "40px",
          height: "40px",
          borderRadius: "50%",
          backgroundColor: "var(--ops-primary-light)",
          color: "var(--ops-primary)",
          display: "flex",
          alignItems: "center",
          justifyContent: "center"
        }}>
          <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
            <rect x="3" y="11" width="18" height="11" rx="2" ry="2"/>
            <path d="M7 11V7a5 5 0 0 1 10 0v4"/>
          </svg>
        </div>
        <h3 style={{ fontSize: "1rem", fontWeight: "700", color: "var(--text-main)", margin: 0 }}>
          Prompt Limit Reached
        </h3>
        <p style={{ fontSize: "0.875rem", color: "var(--text-muted)", margin: "0 0 8px 0", lineHeight: "1.4" }}>
          You've used your 5 free guest prompts. Create an account or sign in to continue chatting with WayFind for free and save your trip history!
        </p>
        <div style={{ display: "flex", gap: "10px" }}>
          <SignInButton mode="modal">
            <button type="button" className="ops-button primary" style={{ minHeight: "36px", padding: "6px 14px", fontSize: "0.85rem" }}>
              Sign In
            </button>
          </SignInButton>
          <SignUpButton mode="modal">
            <button type="button" className="ops-button secondary" style={{ minHeight: "36px", padding: "6px 14px", fontSize: "0.85rem", border: "1px solid var(--ops-border)" }}>
              Sign Up
            </button>
          </SignUpButton>
        </div>
      </div>
    );
  }

  // Handle Enter key: submit when Enter is pressed without Shift
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
        {/* Main input area */}
        <label className="composer-field" htmlFor="message-input">
          <textarea
            ref={textareaRef}
            id="message-input"
            name="message"
            rows="1"
            value={value}
            onChange={(event) => onChange(event.target.value)}
            placeholder="Message WayFind..."
            onKeyDown={handleKeyDown}
          />

          {/* Send button: disabled while pending or when input is empty */}
          <div className="composer-actions">
            <button
              type="submit"
              className="primary-button"
              disabled={pending || !value.trim()}
              title="Send message"
            >
              {/* Small paper-plane like icon */}
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
                <line x1="12" y1="19" x2="12" y2="5"></line>
                <polyline points="5 12 12 5 19 12"></polyline>
              </svg>
            </button>
          </div>
        </label>
      </div>

      {/* Footer hint under the composer. Keep short and helpful. */}
      <div className="composer-footer">
        <p className="composer-hint">WayFind • Developed by Dandelions</p>
      </div>
    </form>
  );
}
