import { useState } from "react";
import Image from "next/image";
import { SignInButton, SignUpButton, UserButton } from "@clerk/nextjs";

function HistoryItem({ session, activeSessionId, onSelectSession, onDeleteSession }) {
  const [dropdownOpen, setDropdownOpen] = useState(false);

  return (
    <div style={{ position: "relative" }}>
      <div
        role="button"
        tabIndex={0}
        className={`history-item ${activeSessionId === session.session_id ? "active" : ""}`}
        onClick={() => {
           onSelectSession(session.session_id);
           setDropdownOpen(false);
        }}
      >
        <span className="history-item-content">
          <span className="history-title">{session.title || "New conversation"}</span>
        </span>
        
        <div style={{ display: "flex", alignItems: "center" }} onClick={(e) => e.stopPropagation()}>
          <button 
             className={`history-options-btn ${dropdownOpen ? "open" : ""}`} 
             onClick={() => setDropdownOpen(!dropdownOpen)}
             title="Options"
          >
            <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
              <circle cx="12" cy="12" r="1"></circle>
              <circle cx="12" cy="5" r="1"></circle>
              <circle cx="12" cy="19" r="1"></circle>
            </svg>
          </button>

          {dropdownOpen && (
            <div className="history-dropdown">
              <button 
                className="history-dropdown-item" 
                onClick={(e) => {
                  e.stopPropagation();
                  alert("Chat link copied to clipboard!");
                  setDropdownOpen(false);
                }}
              >
                Share
              </button>
              <button 
                className="history-dropdown-item danger" 
                onClick={(e) => {
                  e.stopPropagation();
                  onDeleteSession(session.session_id);
                  setDropdownOpen(false);
                }}
              >
                Delete
              </button>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

export default function Sidebar({
  sidebarOpen,
  sessions,
  activeSessionId,
  onSelectSession,
  onDeleteSession,
  onNewChat,
  authState,
  onClose
}) {
  return (
    <>
      <div
        className={`sidebar-backdrop ${sidebarOpen ? "visible" : ""}`}
        onClick={onClose}
        aria-hidden={!sidebarOpen}
      />
      <aside className={`sidebar ${sidebarOpen ? "" : "closed"}`}>
        <div className="sidebar-header" style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', margin: '4px 0 12px 0' }}>
          {/* Logo element representing ChatGPT flower logo */}
          <button style={{ background: 'transparent', border: 'none', cursor: 'pointer', padding: '6px', color: 'var(--text-main)', display: 'flex', alignItems: 'center', justifyContent: 'center', borderRadius: '8px' }} onMouseOver={(e) => e.currentTarget.style.backgroundColor = '#efefef'} onMouseOut={(e) => e.currentTarget.style.backgroundColor = 'transparent'}>
            <Image src="/assets/vana-logo.svg" alt="Vana AI Logo" width={40} height={40} />
          </button>
          
          <button 
            onClick={onClose} 
            style={{ background: 'transparent', border: 'none', cursor: 'pointer', padding: '6px', color: 'var(--text-muted)', borderRadius: '8px', display: 'flex', alignItems: 'center', justifyContent: 'center' }}
            onMouseOver={(e) => e.currentTarget.style.backgroundColor = '#efefef'}
            onMouseOut={(e) => e.currentTarget.style.backgroundColor = 'transparent'}
            title="Close sidebar"
          >
            <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
              <rect x="3" y="3" width="18" height="18" rx="2" ry="2"></rect>
              <line x1="9" y1="3" x2="9" y2="21"></line>
            </svg>
          </button>
        </div>

        <button type="button" className="sidebar-primary" onClick={onNewChat} style={{ marginTop: '8px' }}>
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
            <line x1="12" y1="5" x2="12" y2="19"></line>
            <line x1="5" y1="12" x2="19" y2="12"></line>
          </svg>
          New chat
        </button>

        <section className="sidebar-panel">
          <div className="sidebar-panel-head">Recent Chats</div>
          <div className="history-list">
            {sessions.length ? (
              sessions.map((session) => (
                <HistoryItem 
                  key={session.session_id} 
                  session={session} 
                  activeSessionId={activeSessionId} 
                  onSelectSession={onSelectSession} 
                  onDeleteSession={onDeleteSession}
                />
              ))
            ) : (
              <p style={{ fontSize: '0.8rem', color: 'var(--text-muted)', padding: '8px' }}>No chats yet.</p>
            )}
          </div>
        </section>

        <section className="account-panel">
          <div className="account-actions">
            {authState.user ? (
              <div style={{ display: 'flex', alignItems: 'center', gap: '10px', padding: '4px' }}>
                <UserButton />
                <span style={{ fontSize: '0.875rem', fontWeight: 500, color: 'var(--text-main)' }}>
                   {authState.user.firstName || authState.user.username || "Account"}
                </span>
              </div>
            ) : authState.enabled ? (
              <>
                <SignInButton mode="modal">
                  <button type="button" className="sidebar-secondary">
                    Sign in to sync
                  </button>
                </SignInButton>
                <SignUpButton mode="modal">
                  <button type="button" className="sidebar-secondary subtle">
                    Sign up
                  </button>
                </SignUpButton>
              </>
            ) : (
              <button type="button" className="sidebar-secondary" disabled>
                Guest mode
              </button>
            )}
          </div>
        </section>
      </aside>
    </>
  );
}
