import React, { useEffect, useRef } from "react";

function formatTimestamp(value) {
  const date = new Date(value);
  if (Number.isNaN(date.getTime())) {
    return "";
  }
  return date.toLocaleString([], {
    month: "short",
    day: "numeric",
    hour: "numeric",
    minute: "2-digit"
  });
}

export default function Sidebar({
  sidebarOpen,
  sessions,
  activeSessionId,
  onSelectSession,
  onNewChat,
  authState,
  onSignIn
}) {
  const userButtonRef = useRef(null);

  useEffect(() => {
    if (!authState.clerk || !authState.user || !userButtonRef.current) {
      return;
    }

    authState.clerk.mountUserButton(userButtonRef.current);
    return () => {
      if (userButtonRef.current) {
        userButtonRef.current.innerHTML = "";
      }
    };
  }, [authState.clerk, authState.user]);

  return (
    <aside className={`sidebar ${sidebarOpen ? "open" : ""}`}>
      <div className="brand-block">
        <div className="brand-mark">DT</div>
        <div>
          <p className="brand-kicker">Dandeli Travel</p>
          <h1>Workspace</h1>
        </div>
      </div>

      <button type="button" className="sidebar-action" onClick={onNewChat}>
        New Conversation
      </button>

      <section className="history-panel">
        <div className="panel-head">
          <span>Recent chats</span>
          <span className="panel-meta">{sessions.length}</span>
        </div>

        <div className="history-list">
          {sessions.length ? (
            sessions.map((session) => (
              <button
                key={session.session_id}
                type="button"
                className={`history-item ${activeSessionId === session.session_id ? "active" : ""}`}
                onClick={() => onSelectSession(session.session_id)}
              >
                <span className="history-item-title">{session.title || "New conversation"}</span>
                <p className="history-item-preview">{session.preview || "No messages yet"}</p>
                <p className="history-item-time">{formatTimestamp(session.updated_at)}</p>
              </button>
            ))
          ) : (
            <p className="empty-history">No saved conversations yet. Start a trip planning thread to build your history.</p>
          )}
        </div>
      </section>

      <section className="auth-panel">
        <div className="panel-head">
          <span>Account</span>
        </div>

        {authState.ready ? (
          <>
            <p className="auth-copy">
              {authState.user
                ? `Signed in as ${authState.user.primaryEmailAddress?.emailAddress || authState.user.firstName || "traveler"}.`
                : authState.enabled
                  ? "Sign in to keep your travel planning history tied to your account."
                  : "Guest mode is active. Clerk is ready to plug in once the frontend dependencies are installed and built."}
            </p>
            <div className="auth-slot">
              {authState.user ? (
                <div ref={userButtonRef} />
              ) : authState.enabled ? (
                <button type="button" className="auth-inline-button" onClick={onSignIn}>
                  Sign In
                </button>
              ) : (
                <button type="button" className="auth-inline-button" disabled>
                  Guest Mode
                </button>
              )}
            </div>
          </>
        ) : (
          <p className="auth-copy">Loading account state...</p>
        )}
      </section>
    </aside>
  );
}
