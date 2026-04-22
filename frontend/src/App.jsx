import React, { useEffect, useMemo, useRef, useState } from "react";
import Composer from "./components/Composer";
import MessageList from "./components/MessageList";
import Sidebar from "./components/Sidebar";
import { fetchJson, streamChat } from "./lib/api";
import { ensureGuestUserId, getCurrentUserId, loadClerkInstance } from "./lib/auth";

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

export default function App() {
  const [config, setConfig] = useState({ clerk_enabled: false, clerk_publishable_key: null });
  const [authState, setAuthState] = useState({
    enabled: false,
    ready: false,
    clerk: null,
    user: null
  });
  const [currentUserId, setCurrentUserId] = useState(ensureGuestUserId());
  const [sessions, setSessions] = useState([]);
  const [sessionId, setSessionId] = useState(null);
  const [sessionTitle, setSessionTitle] = useState("Travel Workspace");
  const [messages, setMessages] = useState([
    createMetaMessage("Start with a destination style, budget, activity preference, or booking follow-up.")
  ]);
  const [draft, setDraft] = useState("");
  const [pending, setPending] = useState(false);
  const [status, setStatus] = useState("Loading");
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const listRef = useRef(null);

  useEffect(() => {
    listRef.current?.scrollTo({ top: listRef.current.scrollHeight, behavior: "smooth" });
  }, [messages]);

  async function loadHistory(userId) {
    const data = await fetchJson(`/sessions?user_id=${encodeURIComponent(userId)}`);
    setSessions(data);
    return data;
  }

  async function openSession(targetSessionId, userId) {
    const data = await fetchJson(`/sessions/${targetSessionId}?user_id=${encodeURIComponent(userId)}`);
    setSessionId(data.session_id);
    setSessionTitle(data.title || "Conversation");
    setMessages(
      data.messages.length
        ? data.messages.map((message) => createMessage(message.role, message.content))
        : [createMetaMessage("This conversation is empty. Ask anything about your trip to continue.")]
    );
    setSidebarOpen(false);
  }

  async function refreshCurrentSessionTitle(userId, activeSessionId) {
    if (!activeSessionId) {
      return;
    }
    const data = await fetchJson(`/sessions/${activeSessionId}?user_id=${encodeURIComponent(userId)}`);
    setSessionTitle(data.title || "Conversation");
  }

  async function bootUserState(userId) {
    setCurrentUserId(userId);
    setSessionId(null);
    setSessionTitle("Travel Workspace");
    setMessages([createMetaMessage("Start with a destination style, budget, activity preference, or booking follow-up.")]);
    const sessionList = await loadHistory(userId);
    if (sessionList.length) {
      await openSession(sessionList[0].session_id, userId);
    }
  }

  useEffect(() => {
    async function init() {
      try {
        const configData = await fetchJson("/config");
        setConfig(configData);

        if (configData.clerk_enabled && configData.clerk_publishable_key) {
          const clerk = await loadClerkInstance(configData.clerk_publishable_key);
          if (clerk) {
            const applyAuthState = async () => {
              const userId = getCurrentUserId(clerk);
              setAuthState({
                enabled: true,
                ready: true,
                clerk,
                user: clerk.user || null
              });
              await bootUserState(userId);
              setStatus("Ready");
            };

            clerk.addListener(applyAuthState);
            await applyAuthState();
            return;
          }
        }

        setAuthState({
          enabled: false,
          ready: true,
          clerk: null,
          user: null
        });
        await bootUserState(ensureGuestUserId());
        setStatus("Ready");
      } catch (error) {
        console.error(error);
        setStatus("Error");
        setMessages([createMetaMessage("The workspace could not finish loading. Check the backend and try again.")]);
      }
    }

    init();
  }, []);

  async function handleNewChat() {
    setPending(true);
    try {
      const data = await fetchJson("/sessions", {
        method: "POST",
        body: JSON.stringify({
          user_id: currentUserId,
          title: "New conversation"
        })
      });
      setSessionId(data.session_id);
      setSessionTitle(data.title || "New conversation");
      setMessages([createMetaMessage("New conversation ready. Ask about stays, prices, activities, or bookings.")]);
      await loadHistory(currentUserId);
      setSidebarOpen(false);
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
        title: "New conversation"
      })
    });
    setSessionId(data.session_id);
    setSessionTitle(data.title || "New conversation");
    return data.session_id;
  }

  async function handleReset() {
    if (!sessionId) {
      setMessages([createMetaMessage("New conversation ready. Ask about stays, prices, activities, or bookings.")]);
      return;
    }

    setPending(true);
    try {
      await fetch(`/sessions/${sessionId}?user_id=${encodeURIComponent(currentUserId)}`, {
        method: "DELETE"
      });
      setMessages([createMetaMessage("Conversation cleared. You can start fresh from here.")]);
      setSessionTitle("New conversation");
      await loadHistory(currentUserId);
    } finally {
      setPending(false);
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
    setStatus("Working");
    setMessages((prev) => [
      ...prev,
      userMessage,
      { id: assistantId, role: "assistant", content: "", streaming: true }
    ]);

    try {
      const activeSessionId = await ensureSession();
      const reply = await streamChat(
        {
          session_id: activeSessionId,
          user_id: currentUserId,
          message: content
        },
        {
          onSession: (nextSessionId) => {
            setSessionId(nextSessionId);
          },
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
            ? { ...message, content: reply || "I couldn't produce a reply right now.", streaming: false }
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
      setStatus("Error");
    } finally {
      setPending(false);
    }
  }

  const headerChips = useMemo(
    () => ["Stay research", "Trip planning", "Resort details", "Booking follow-up"],
    []
  );

  return (
    <div className="app-frame">
      <Sidebar
        sidebarOpen={sidebarOpen}
        sessions={sessions}
        activeSessionId={sessionId}
        onSelectSession={(nextSessionId) => openSession(nextSessionId, currentUserId)}
        onNewChat={handleNewChat}
        authState={authState}
        onSignIn={() =>
          authState.clerk?.openSignIn({
            afterSignInUrl: window.location.href,
            afterSignUpUrl: window.location.href
          })
        }
      />

      <main className="workspace">
        <header className="topbar">
          <button type="button" className="icon-button" onClick={() => setSidebarOpen((value) => !value)}>
            Menu
          </button>
          <div>
            <p className="eyebrow">Human-centered travel desk</p>
            <h2>{sessionTitle}</h2>
          </div>
          <span className="pill">{status}</span>
        </header>

        <section className="hero-strip">
          <div>
            <p className="hero-label">Planning Console</p>
            <h3>Organize trip research, compare resorts, and keep every travel conversation in one calm workspace.</h3>
          </div>
          <div className="hero-note">
            {headerChips.map((chip) => (
              <span key={chip}>{chip}</span>
            ))}
          </div>
        </section>

        <section className="chat-shell">
          <div ref={listRef} className="chat-scroll">
            <MessageList messages={messages} />
          </div>
          <Composer
            value={draft}
            onChange={setDraft}
            onSubmit={handleSubmit}
            onReset={handleReset}
            pending={pending}
          />
        </section>
      </main>
    </div>
  );
}
