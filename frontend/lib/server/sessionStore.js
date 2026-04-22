import { randomUUID } from "crypto";
import { getMongoDb } from "./mongodb";
import { loadFileStore, saveFileStore } from "./fileSessionStore";

export const DEFAULT_USER_ID = "guest-local";

function utcNow() {
  return new Date().toISOString().replace(/\.\d{3}Z$/, "Z");
}

export function normalizeUserId(userId) {
  const cleaned = `${userId || ""}`.trim();
  return cleaned || DEFAULT_USER_ID;
}

function summarizeSession(sessionId, session) {
  const lastUserMessage = [...(session.messages || [])]
    .reverse()
    .find((message) => message.role === "user");

  return {
    session_id: sessionId,
    title: session.title || "New conversation",
    preview: lastUserMessage ? `${lastUserMessage.content || ""}`.trim().slice(0, 80) : "",
    updated_at: session.updated_at || utcNow()
  };
}

export async function getUsersCollection() {
  const db = await getMongoDb();
  if (!db) {
    return null;
  }
  return db.collection("chat_users");
}

export async function ensureUserDocument(userId, profile = {}) {
  const normalizedUserId = normalizeUserId(userId);
  const collection = await getUsersCollection();
  const now = utcNow();

  if (!collection) {
    const store = await loadFileStore();
    if (!store[normalizedUserId]) {
      store[normalizedUserId] = {
        user_id: normalizedUserId,
        created_at: now,
        updated_at: now,
        profile: {},
        sessions: {}
      };
    }
    if (profile.user_name) {
      store[normalizedUserId].profile.name = profile.user_name;
    }
    if (profile.user_email) {
      store[normalizedUserId].profile.email = profile.user_email;
    }
    store[normalizedUserId].updated_at = now;
    await saveFileStore(store);
    return store[normalizedUserId];
  }

  await collection.updateOne(
    { _id: normalizedUserId },
    {
      $setOnInsert: {
        _id: normalizedUserId,
        user_id: normalizedUserId,
        created_at: now,
        sessions: {}
      },
      $set: {
        updated_at: now,
        ...(profile.user_name ? { "profile.name": profile.user_name } : {}),
        ...(profile.user_email ? { "profile.email": profile.user_email } : {})
      }
    },
    { upsert: true }
  );

  return collection.findOne({ _id: normalizedUserId });
}

export async function listSessions(userId) {
  const user = await ensureUserDocument(userId);
  const sessions = Object.entries(user?.sessions || {}).map(([sessionId, session]) =>
    summarizeSession(sessionId, session)
  );
  sessions.sort((a, b) => `${b.updated_at}`.localeCompare(`${a.updated_at}`));
  return sessions;
}

export async function getSession(userId, sessionId) {
  const user = await ensureUserDocument(userId);
  const session = user?.sessions?.[sessionId];
  if (!session) {
    return null;
  }
  return {
    session_id: sessionId,
    title: session.title || "New conversation",
    updated_at: session.updated_at || utcNow(),
    messages: session.messages || []
  };
}

export async function createSession(userId, title = "New conversation", profile = {}) {
  const normalizedUserId = normalizeUserId(userId);
  const sessionId = randomUUID();
  const now = utcNow();
  const collection = await getUsersCollection();

  await ensureUserDocument(normalizedUserId, profile);
  await collection.updateOne(
    { _id: normalizedUserId },
    {
      $set: {
        [`sessions.${sessionId}`]: {
          title,
          updated_at: now,
          messages: []
        },
        updated_at: now
      }
    }
  );

  return {
    session_id: sessionId,
    title
  };
}

export async function saveSession(userId, sessionId, session, profile = {}) {
  const normalizedUserId = normalizeUserId(userId);
  const collection = await getUsersCollection();
  const user = await ensureUserDocument(normalizedUserId, profile);
  if (!collection) {
    const store = await loadFileStore();
    const nextUser = store[normalizedUserId] || user || {
      user_id: normalizedUserId,
      profile: {},
      sessions: {}
    };
    nextUser.profile = nextUser.profile || {};
    if (profile.user_name) {
      nextUser.profile.name = profile.user_name;
    }
    if (profile.user_email) {
      nextUser.profile.email = profile.user_email;
    }
    nextUser.sessions = nextUser.sessions || {};
    nextUser.sessions[sessionId] = session;
    nextUser.updated_at = utcNow();
    store[normalizedUserId] = nextUser;
    await saveFileStore(store);
    return;
  }
  await collection.updateOne(
    { _id: normalizedUserId },
    {
      $set: {
        [`sessions.${sessionId}`]: session,
        updated_at: utcNow(),
        ...(profile.user_name ? { "profile.name": profile.user_name } : {}),
        ...(profile.user_email ? { "profile.email": profile.user_email } : {})
      }
    }
  );
}

export async function getOrCreateSession(userId, sessionId, title = "New conversation", profile = {}) {
  const normalizedUserId = normalizeUserId(userId);
  if (sessionId) {
    const existing = await getSession(normalizedUserId, sessionId);
    if (existing) {
      return [sessionId, { title: existing.title, updated_at: existing.updated_at, messages: existing.messages }];
    }
  }

  const created = await createSession(normalizedUserId, title, profile);
  return [created.session_id, { title: created.title, updated_at: utcNow(), messages: [] }];
}

export async function clearSession(userId, sessionId) {
  const normalizedUserId = normalizeUserId(userId);
  const session = await getSession(normalizedUserId, sessionId);
  if (!session) {
    return null;
  }

  const nextSession = {
    title: "New conversation",
    updated_at: utcNow(),
    messages: []
  };
  await saveSession(normalizedUserId, sessionId, nextSession);
  return nextSession;
}

export function recordMessage(session, role, content) {
  const nextSession = {
    ...session,
    title: session.title || "New conversation",
    updated_at: utcNow(),
    messages: [...(session.messages || []), { role, content, created_at: utcNow() }]
  };

  if (role === "user" && (!session.title || session.title === "New conversation")) {
    const compact = `${content}`.trim().replace(/\s+/g, " ");
    nextSession.title = compact.slice(0, 48) + (compact.length > 48 ? "..." : "");
  }

  return nextSession;
}
