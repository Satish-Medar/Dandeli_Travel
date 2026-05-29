/*
  Main chat page for interacting with the WayFind travel assistant.

  Simple overview:
  - This file renders the chat UI, message thread, composer, and sidebar.
  - It handles user sessions, guest mode, session history, and streaming replies.
  - Most network work is done through `fetchJson` and `streamChat` helpers.
*/
/* File: frontend/app/chat/page.jsx */

"use client";

import { useEffect, useMemo, useRef, useState } from "react";
import { useRouter } from "next/navigation";
import { useUser } from "@clerk/nextjs";
import Composer from "../../components/Composer";
import MessageThread from "../../components/MessageThread";
import Sidebar from "../../components/Sidebar";
import { fetchJson, streamChat } from "../../lib/api";
import { ensureGuestUserId } from "../../lib/auth";

// Create a non-interactive status message shown inside the chat thread.
function createMetaMessage(content) {
  return {
    id: crypto.randomUUID(),
    role: "meta",
    content,
  };
}

// Create a normal message with a role of user or assistant.
function createMessage(role, content, extra = {}) {
  return {
    id: crypto.randomUUID(),
    role,
    content,
    ...extra,
  };
}

function createInitialMessage() {
  return createMetaMessage(
    "Ask about resorts, trip plans, prices, or bookings.",
  );
}

// Extract a simple auth profile object from the Clerk user object.
function getAuthProfile(user) {
  if (!user) {
    return {
      user_name: null,
      user_email: null,
    };
  }

  return {
    user_name:
      [user.firstName, user.lastName].filter(Boolean).join(" ").trim() ||
      user.username ||
      null,
    user_email: user.primaryEmailAddress?.emailAddress || null,
  };
}

// Main chat page component.
// This component is responsible for session state, message updates, and UI layout.
export default function Page() {
  const router = useRouter();
  const { isLoaded, isSignedIn, user } = useUser();
  const [config, setConfig] = useState({
    clerk_enabled: false,
    clerk_publishable_key: null,
  });
  const [authState, setAuthState] = useState({
    enabled: false,
    ready: false,
    clerk: null,
    user: null,
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
  const isGuest = authState.ready && !authState.user;
  const [promptCount, setPromptCount] = useState(0);

  useEffect(() => {
    if (typeof window !== "undefined") {
      const stored = localStorage.getItem("wayfind_guest_prompt_count");
      if (stored) {
        setPromptCount(parseInt(stored, 10));
      }
    }
  }, []);

  useEffect(() => {
    // Close sidebar on mobile by default to prioritize chat viewport
    if (typeof window !== "undefined") {
      if (window.innerWidth <= 768) {
        setSidebarOpen(false);
      }
    }
    const handleResizeSidebar = () => {
      if (window.innerWidth > 768) {
        setSidebarOpen(true);
      }
    };
    window.addEventListener("resize", handleResizeSidebar);
    return () => window.removeEventListener("resize", handleResizeSidebar);
  }, []);

  // Scroll the chat thread to the bottom whenever messages change.
  useEffect(() => {
    threadRef.current?.scrollTo({
      top: threadRef.current.scrollHeight,
      behavior: "smooth",
    });
  }, [messages]);

  // Load the user's saved chat session list from the backend.
  async function loadHistory(userId) {
    if (isGuest) {
      setSessions([]);
      setSessionCount(0);
      return [];
    }

    const data = await fetchJson(
      `/sessions?user_id=${encodeURIComponent(userId)}`,
    );
    setSessions(data);
    setSessionCount(data.length);
    return data;
  }

  // Open a saved conversation session and load its messages.
  async function openSession(targetSessionId, userId) {
    if (isGuest) {
      setSessionId(null);
      setSessionTitle("Untitled trip thread");
      setMessages([createInitialMessage()]);
      setSidebarOpen(false);
      return;
    }

    const data = await fetchJson(
      `/sessions/${targetSessionId}?user_id=${encodeURIComponent(userId)}`,
    );
    setSessionId(data.session_id);
    setSessionTitle(data.title || "Untitled trip thread");
    setMessages(
      data.messages.length
        ? data.messages.map((message) =>
            createMessage(message.role, message.content),
          )
        : [
            createMetaMessage(
              "This conversation is empty. Ask anything about your Dandeli trip to continue.",
            ),
          ],
    );
    setSidebarOpen(false);
  }

  async function refreshCurrentSessionTitle(userId, activeSessionId) {
    if (isGuest || !activeSessionId) {
      return;
    }
    const data = await fetchJson(
      `/sessions/${activeSessionId}?user_id=${encodeURIComponent(userId)}`,
    );
    setSessionTitle(data.title || "Untitled trip thread");
  }

  // Initialize chat state when a user or guest session boots.
  async function bootUserState(userId) {
    setCurrentUserId(userId);
    setSessionId(null);
    setSessionTitle("Untitled trip thread");
    setMessages([createInitialMessage()]);
    if (!isGuest) {
      const sessionList = await loadHistory(userId);
      if (sessionList.length) {
        await openSession(sessionList[0].session_id, userId);
      }
    }
  }

  useEffect(() => {
    async function fetchConfig() {
      try {
        const configData = await fetchJson("/config");
        setConfig(configData);
      } catch (error) {
        console.error("fetchConfig failed:", error);
        setStatus("Unavailable");
        setMessages([
          createMetaMessage(
            "The workspace could not load. Check whether the backend is running.",
          ),
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
          user: user,
        });
        await bootUserState(user.id);
      } else {
        setAuthState({
          enabled: true,
          ready: true,
          clerk: null,
          user: null,
        });
        await bootUserState(ensureGuestUserId());
      }
      setStatus("Ready");
      setBooted(true);
    }

    applyAuth();
  }, [isLoaded, isSignedIn, user, booted, status]);

  // Create a brand new chat session, clearing the current conversation.
  async function handleNewChat() {
    setPending(true);
    try {
      if (!isGuest) {
        const data = await fetchJson("/sessions", {
          method: "POST",
          body: JSON.stringify({
            user_id: currentUserId,
            title: "New conversation",
            ...getAuthProfile(authState.user),
          }),
        });
        setSessionId(data.session_id);
        setSessionTitle(data.title || "New conversation");
        await loadHistory(currentUserId);
      } else {
        setSessionId(null);
        setSessionTitle("New conversation");
      }

      setMessages([createMetaMessage("New conversation ready.")]);
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

    if (isGuest) {
      const guestSessionId = crypto.randomUUID();
      setSessionId(guestSessionId);
      setSessionTitle("New conversation");
      return guestSessionId;
    }

    const data = await fetchJson("/sessions", {
      method: "POST",
      body: JSON.stringify({
        user_id: currentUserId,
        title: "New conversation",
        ...getAuthProfile(authState.user),
      }),
    });
    setSessionId(data.session_id);
    setSessionTitle(data.title || "New conversation");
    return data.session_id;
  }

  async function handleReset() {
    if (!sessionId || isGuest) {
      setSessionId(null);
      setMessages([createMetaMessage("New conversation ready.")]);
      setSessionTitle("New conversation");
      return;
    }

    setPending(true);
    try {
      await fetchJson(
        `/sessions/${sessionId}?user_id=${encodeURIComponent(currentUserId)}`,
        {
          method: "DELETE",
        },
      );
      setMessages([createMetaMessage("Conversation cleared.")]);
      setSessionTitle("New conversation");
      await loadHistory(currentUserId);
      setStatus("Ready");
    } finally {
      setPending(false);
    }
  }

  async function handleDeleteSession(targetSessionId) {
    if (isGuest) {
      setSessionId(null);
      setSessionTitle("New conversation");
      setMessages([createInitialMessage()]);
      return;
    }

    try {
      await fetchJson(
        `/sessions/${targetSessionId}?user_id=${encodeURIComponent(currentUserId)}`,
        {
          method: "DELETE",
        },
      );
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

  // Send the current user draft to the assistant and stream the reply.
  async function handleSubmit() {
    const content = draft.trim();
    if (!content || pending) {
      return;
    }

    if (isGuest && promptCount >= 5) {
      return;
    }

    if (isGuest) {
      const nextCount = promptCount + 1;
      setPromptCount(nextCount);
      if (typeof window !== "undefined") {
        localStorage.setItem("wayfind_guest_prompt_count", String(nextCount));
      }
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
        streaming: true,
      },
    ]);

    try {
      const activeSessionId = await ensureSession();
      const sessionMessages = messages
        .filter((message) => message.role !== "meta" && message.content)
        .map(({ role, content, name }) => ({
          role,
          content,
          name: name || "",
        }));

      const reply = await streamChat(
        {
          session_id: activeSessionId,
          user_id: currentUserId,
          message: content,
          messages: sessionMessages,
          persist_history: !isGuest,
          ...getAuthProfile(authState.user),
        },
        {
          onSession: (nextSessionId) => setSessionId(nextSessionId),
          onChunk: (partialReply) => {
            setMessages((prev) =>
              prev.map((message) =>
                message.id === assistantId
                  ? { ...message, content: partialReply, streaming: true }
                  : message,
              ),
            );
          },
        },
      );

      setMessages((prev) =>
        prev.map((message) =>
          message.id === assistantId
            ? {
                ...message,
                content: reply || "I could not produce a response right now.",
                streaming: false,
              }
            : message,
        ),
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
                content:
                  "The assistant could not respond right now. Please try again in a moment.",
                streaming: false,
              }
            : message,
        ),
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
        onSelectSession={(nextSessionId) =>
          openSession(nextSessionId, currentUserId)
        }
        onDeleteSession={handleDeleteSession}
        onNewChat={handleNewChat}
        authState={authState}
        onClose={() => setSidebarOpen(false)}
        noBackdrop={true}
      />

      <main className="workspace">
        <div className="chat-topbar">
          <div className="chat-topbar-left">
            {!sidebarOpen && (
              <button
                className="sidebar-toggle-btn"
                onClick={() => setSidebarOpen(true)}
                title="Expand sidebar"
              >
                <svg
                  width="18"
                  height="18"
                  viewBox="0 0 24 24"
                  fill="none"
                  stroke="currentColor"
                  strokeWidth="2.5"
                  strokeLinecap="round"
                  strokeLinejoin="round"
                >
                  <rect x="3" y="3" width="18" height="18" rx="2" ry="2"></rect>
                  <line x1="9" y1="3" x2="9" y2="21"></line>
                </svg>
              </button>
            )}

            {!sidebarOpen ? (
              <a href="/" className="chat-topbar-brand-logo">
                <img
                  src="/assets/Gemini_Generated_Image.png"
                  alt="WayFind Logo"
                  width={44}
                  height={44}
                  style={{ objectFit: "contain", borderRadius: "8px" }}
                />
                <span>WayFind</span>
              </a>
            ) : (
              <span className="chat-topbar-session-title">{sessionTitle}</span>
            )}
          </div>

          <div className="chat-topbar-actions">
            <span className={`status-pill ${status.toLowerCase()}`}>
              {status}
            </span>
          </div>
        </div>

        <section className="thread-shell">
          <div ref={threadRef} className="thread-scroll">
            <MessageThread messages={messages} />
          </div>
          <div className="composer-gradient-mask" />
          <Composer
            value={draft}
            onChange={setDraft}
            onSubmit={handleSubmit}
            onReset={handleReset}
            pending={pending}
            sessionTitle={sessionTitle}
            clerkEnabled={config.clerk_enabled}
            isLimitReached={isGuest && promptCount >= 5}
          />
        </section>
      </main>
    </div>
  );
}
