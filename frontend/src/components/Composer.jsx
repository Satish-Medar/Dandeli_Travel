import React from "react";

export default function Composer({
  value,
  onChange,
  onSubmit,
  onReset,
  pending
}) {
  return (
    <form
      className="composer"
      onSubmit={(event) => {
        event.preventDefault();
        onSubmit();
      }}
    >
      <label className="composer-box" htmlFor="message-input">
        <textarea
          id="message-input"
          name="message"
          rows="1"
          value={value}
          onChange={(event) => onChange(event.target.value)}
          placeholder="Plan a weekend, compare stays, ask for contact details, or continue a trip conversation..."
          onKeyDown={(event) => {
            if (event.key === "Enter" && !event.shiftKey) {
              event.preventDefault();
              onSubmit();
            }
          }}
        />
        <div className="composer-actions">
          <button type="button" className="ghost-button" onClick={onReset} disabled={pending}>
            Clear Chat
          </button>
          <button type="submit" className="primary-button" disabled={pending}>
            {pending ? "Working..." : "Send"}
          </button>
        </div>
      </label>
    </form>
  );
}
