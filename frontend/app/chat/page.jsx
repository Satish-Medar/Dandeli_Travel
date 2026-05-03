"use client";

import { useEffect, useMemo, useRef, useState } from "react";
import { useRouter } from "next/navigation";
import { useUser } from "@clerk/nextjs";
import Composer from "../../components/Composer";
import MessageThread from "../../components/MessageThread";
import Sidebar from "../../components/Sidebar";
import { fetchJson, streamChat } from "../../lib/api";
import { ensureGuestUserId } from "../../lib/auth";

function createMetaMessage(content) {
  return {
    id: crypto.randomUUID(),
    role: "meta",
    content
  };
}

function createMessage(role, content, extra = {}) {
  return {
    id: crypto.randomUUID(),
    role,
    content,
    ...extra
  };
}

function createInitialMessage() {
  return createMetaMessage(
    "Ask about resorts, trip plans, prices, or bookings."
  );
}

function getAuthProfile(user) {
  if (!user) {
    return {
      user_name: null,
      user_email: null
    };
  }

  return {
    user_name: [user.firstName, user.lastName].filter(Boolean).join(" ").trim() || user.username || null,
    user_email: user.primaryEmailAddress?.emailAddress || null
  };
}

export default function Page() {
  const router = useRouter();
  const { isLoaded, isSignedIn, user } = useUser();
  const [config, setConfig] = useState({ clerk_enabled: false, clerk_publishable_key: null });
  const [authState, setAuthState] = useState({
    enabled: false,
    ready: false,
    clerk: null,
    user: null
  });
  const [booted, setBooted] = useState(false);
  const [currentUserId, setCurrentUserId] = useState("guest-local");
  const [sessions, setSessions] = useState([]);
  const [sessionId, setSessionId] = useState(null);
  const [sessionTitle, setSessionTitle] = useState("Untitled trip thread");
  const [messages, setMessages] = useState([createInitialMessage()]);
  const [draft, setDraft] = useState("");
  const [pending, setPending] = useState(false);
  const [status, setStatus] = useState("Loading");
  const [sidebarOpen, setSidebarOpen] = useState(true);
  const [sessionCount, setSessionCount] = useState(0);
  const threadRef = useRef(null);

  useEffect(() => {
    threadRef.current?.scrollTo({
      top: threadRef.current.scrollHeight,
      behavior: "smooth"
    });
  }, [messages]);

  async function loadHistory(userId) {
    const data = await fetchJson(`/sessions?user_id=${encodeURIComponent(userId)}`);
    setSessions(data);
    setSessionCount(data.length);
    return data;
  }

  async function openSession(targetSessionId, userId) {
    const data = await fetchJson(`/sessions/${targetSessionId}?user_id=${encodeURIComponent(userId)}`);
    setSessionId(data.session_id);
    setSessionTitle(data.title || "Untitled trip thread");
    setMessages(
      data.messages.length
        ? data.messages.map((message) => createMessage(message.role, message.content))
        : [createMetaMessage("This conversation is empty. Ask anything about your Dandeli trip to continue.")]
    );
    setSidebarOpen(false);
  }

  async function refreshCurrentSessionTitle(userId, activeSessionId) {
    if (!activeSessionId) {
      return;
    }
    const data = await fetchJson(`/sessions/${activeSessionId}?user_id=${encodeURIComponent(userId)}`);
    setSessionTitle(data.title || "Untitled trip thread");
  }

  async function bootUserState(userId) {
    setCurrentUserId(userId);
    setSessionId(null);
    setSessionTitle("Untitled trip thread");
    setMessages([createInitialMessage()]);
    const sessionList = await loadHistory(userId);
    if (sessionList.length) {
      await openSession(sessionList[0].session_id, userId);
    }
  }

  useEffect(() => {
    async function fetchConfig() {
      try {
        const configData = await fetchJson("/config");
        setConfig(configData);
      } catch (error) {
        console.error(error);
        setStatus("Unavailable");
        setMessages([
          createMetaMessage("The workspace could not load. Check whether the backend is running.")
        ]);
      }
    }
    fetchConfig();
  }, []);

  useEffect(() => {
    if (!isLoaded || booted || status === "Unavailable") return;
    
    async function applyAuth() {
      if (isSignedIn && user) {
        setAuthState({
          enabled: true,
          ready: true,
          clerk: {},
          user: user
        });
        await bootUserState(user.id);
      } else {
        setAuthState({
          enabled: true,
          ready: true,
          clerk: null,
          user: null
        });
        await bootUserState(ensureGuestUserId());
      }
      setStatus("Ready");
      setBooted(true);
    }
    
    applyAuth();
  }, [isLoaded, isSignedIn, user, booted, status]);

  async function handleNewChat() {
    setPending(true);
    try {
      const data = await fetchJson("/sessions", {
        method: "POST",
        body: JSON.stringify({
          user_id: currentUserId,
          title: "New conversation",
          ...getAuthProfile(authState.user)
        })
      });
      setSessionId(data.session_id);
      setSessionTitle(data.title || "New conversation");
      setMessages([
        createMetaMessage("New conversation ready.")
      ]);
      await loadHistory(currentUserId);
      setSidebarOpen(false);
      setStatus("Ready");
    } finally {
      setPending(false);
    }
  }

  async function ensureSession() {
    if (sessionId) {
      return sessionId;
    }

    const data = await fetchJson("/sessions", {
      method: "POST",
      body: JSON.stringify({
        user_id: currentUserId,
        title: "New conversation",
        ...getAuthProfile(authState.user)
      })
    });
    setSessionId(data.session_id);
    setSessionTitle(data.title || "New conversation");
    return data.session_id;
  }

  async function handleReset() {
    if (!sessionId) {
      setMessages([
        createMetaMessage("New conversation ready.")
      ]);
      return;
    }

    setPending(true);
    try {
      await fetchJson(`/sessions/${sessionId}?user_id=${encodeURIComponent(currentUserId)}`, {
        method: "DELETE"
      });
      setMessages([
        createMetaMessage("Conversation cleared.")
      ]);
      setSessionTitle("New conversation");
      await loadHistory(currentUserId);
      setStatus("Ready");
    } finally {
      setPending(false);
    }
  }

  async function handleDeleteSession(targetSessionId) {
    try {
      await fetchJson(`/sessions/${targetSessionId}?user_id=${encodeURIComponent(currentUserId)}`, {
        method: "DELETE"
      });
      await loadHistory(currentUserId);
      if (sessionId === targetSessionId) {
        setSessionId(null);
        setSessionTitle("New conversation");
        setMessages([createInitialMessage()]);
      }
    } catch (error) {
      console.error("Failed to delete session", error);
    }
  }

  async function handleSubmit() {
    const content = draft.trim();
    if (!content || pending) {
      return;
    }

    const userMessage = createMessage("user", content);
    const assistantId = crypto.randomUUID();

    setDraft("");
    setPending(true);
    setStatus("Thinking");
    setMessages((prev) => [
      ...prev,
      userMessage,
      {
        id: assistantId,
        role: "assistant",
        content: "",
        streaming: true
      }
    ]);

    try {
      const activeSessionId = await ensureSession();
      const reply = await streamChat(
        {
          session_id: activeSessionId,
          user_id: currentUserId,
          message: content,
          ...getAuthProfile(authState.user)
        },
        {
          onSession: (nextSessionId) => setSessionId(nextSessionId),
          onChunk: (partialReply) => {
            setMessages((prev) =>
              prev.map((message) =>
                message.id === assistantId
                  ? { ...message, content: partialReply, streaming: true }
                  : message
              )
            );
          }
        }
      );

      setMessages((prev) =>
        prev.map((message) =>
          message.id === assistantId
            ? {
                ...message,
                content: reply || "I could not produce a response right now.",
                streaming: false
              }
            : message
        )
      );

      await loadHistory(currentUserId);
      await refreshCurrentSessionTitle(currentUserId, activeSessionId);
      setStatus("Ready");
    } catch (error) {
      console.error(error);
      setMessages((prev) =>
        prev.map((message) =>
          message.id === assistantId
            ? {
                ...message,
                content: "The assistant could not respond right now. Please try again in a moment.",
                streaming: false
              }
            : message
        )
      );
      setStatus("Unavailable");
    } finally {
      setPending(false);
    }
  }

  const subtitle = useMemo(() => {
    if (status === "Thinking") {
      return "Thinking";
    }
    if (sessionCount) {
      return `${sessionCount} ${sessionCount === 1 ? "chat" : "chats"}`;
    }
    return "Ready";
  }, [sessionCount, status]);

  return (
    <div className="shell">
      <Sidebar
        sidebarOpen={sidebarOpen}
        sessions={sessions}
        activeSessionId={sessionId}
        onSelectSession={(nextSessionId) => openSession(nextSessionId, currentUserId)}
        onDeleteSession={handleDeleteSession}
        onNewChat={handleNewChat}
        authState={authState}
        onClose={() => setSidebarOpen(false)}
      />

      <main className="workspace">
        {!sidebarOpen && (
          <button className="open-sidebar-btn" onClick={() => setSidebarOpen(true)} title="Open sidebar">
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
              <rect x="3" y="3" width="18" height="18" rx="2" ry="2"></rect>
              <line x1="9" y1="3" x2="9" y2="21"></line>
            </svg>
          </button>
        )}
        
        <div style={{ 
            display: 'flex', justifyContent: 'space-between', alignItems: 'center', 
            padding: '12px 16px', position: 'sticky', top: 0, zIndex: 10, background: 'var(--bg)' 
        }}>
          <div style={{ display: 'flex', alignItems: 'center', marginLeft: sidebarOpen ? '0' : '40px' }}>
             <button style={{ 
               display: 'flex', alignItems: 'center', gap: '4px', background: 'transparent', 
               border: 'none', cursor: 'pointer', padding: '6px 10px', borderRadius: '8px',
               color: 'var(--text-main)', fontSize: '1.125rem', fontWeight: 600
             }} onMouseOver={(e) => e.currentTarget.style.backgroundColor = '#efefef'} onMouseOut={(e) => e.currentTarget.style.backgroundColor = 'transparent'}>
               Vana AI
               <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" style={{ color: 'var(--text-muted)' }}>
                 <polyline points="6 9 12 15 18 9"></polyline>
               </svg>
             </button>
          </div>

          <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
            <span className={`status-pill ${status.toLowerCase()}`}>{status}</span>
            <button style={{ 
               display: 'flex', alignItems: 'center', gap: '6px', 
               padding: '8px 12px', borderRadius: '9999px', 
               backgroundColor: '#F3F0FF', color: '#6B4CFF', 
               fontWeight: 600, fontSize: '0.875rem', border: 'none', cursor: 'pointer' 
            }} onMouseOver={(e) => e.currentTarget.style.opacity = '0.9'} onMouseOut={(e) => e.currentTarget.style.opacity = '1'}>
              <svg width="14" height="14" viewBox="0 0 24 24" fill="currentColor">
                <path d="M12 2l2.4 7.4L22 10.6l-6.2 5.5 1.8 7.9L12 19l-5.6 5 1.8-7.9-6.2-5.5 7.6-1.2L12 2z"></path>
              </svg>
              Get Plus
            </button>
            {/* <button style={{ background: 'transparent', border: 'none', cursor: 'pointer', display: 'flex', alignItems: 'center', padding: '4px', color: 'var(--text-muted)' }}>
               <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                 <circle cx="12" cy="12" r="10"></circle>
                 <circle cx="12" cy="10" r="3"></circle>
                 <path d="M7 20.662V19a2 2 0 012-2h6a2 2 0 012 2v1.662"></path>
               </svg>
            </button> */}
          </div>
        </div>

        <section className="thread-shell">
          <div ref={threadRef} className="thread-scroll">
            <MessageThread messages={messages} />
          </div>
          <Composer
            value={draft}
            onChange={setDraft}
            onSubmit={handleSubmit}
            onReset={handleReset}
            pending={pending}
            sessionTitle={sessionTitle}
            clerkEnabled={config.clerk_enabled}
          />
        </section>
      </main>
    </div>
  );
}
