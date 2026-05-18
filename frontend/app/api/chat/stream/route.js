/* Streaming chat API route for conversational messages. */
/* File: frontend/app/api/chat/stream/route.js */


import {
  getOrCreateSession,
  normalizeUserId,
  recordMessage,
  saveSession,
} from "../../../../lib/server/sessionStore";
import { requestAssistantReply } from "../../../../lib/server/pythonApi";

export const runtime = "nodejs";

function toSseMessage(event, data) {
  return `event: ${event}\ndata: ${data}\n\n`;
}

function tokenizeReply(reply) {
  const matches = reply.match(/\S+\s*|\n/g);
  return matches?.length ? matches : [reply];
}

export async function POST(request) {
  const payload = await request.json();
  const userId = normalizeUserId(payload.user_id);
  const profile = {
    user_name: payload.user_name,
    user_email: payload.user_email,
  };
  const shouldPersist = payload.persist_history !== false;

  let sessionId = payload.session_id || null;
  let session;

  if (shouldPersist) {
    const result = await getOrCreateSession(
      userId,
      sessionId,
      "New conversation",
      profile,
    );
    sessionId = result[0];
    session = result[1];
  } else {
    session = {
      title: "New conversation",
      updated_at: new Date().toISOString().replace(/\.\d{3}Z$/, "Z"),
      messages: (payload.messages || [])
        .filter((message) => message.role === "user" || message.role === "assistant")
        .map(({ role, content, name }) => ({
          role,
          content,
          name: name || "",
          created_at: new Date().toISOString().replace(/\.\d{3}Z$/, "Z"),
        })),
    };
  }

  const withUserMessage = recordMessage(
    session,
    "user",
    `${payload.message || ""}`.trim(),
  );

  let reply,
    nodeName = "";
  try {
    const response = await requestAssistantReply({
      messages: withUserMessage.messages
        .slice(0, -1)
        .map(({ role, content, name }) => ({
          role,
          content,
          name: name || "",
        })),
      message: payload.message,
    });
    reply = response.reply;
    nodeName = response.nodeName;
  } catch (error) {
    console.error("Assistant request failed:", error);
    reply =
      error?.message ||
      "I'm having trouble reaching one of the AI services right now. Please try again in a moment.";
  }

  const finalSession = recordMessage(
    withUserMessage,
    "assistant",
    reply,
    nodeName,
  );
  if (shouldPersist) {
    await saveSession(userId, sessionId, finalSession, profile);
  }

  const encoder = new TextEncoder();
  const stream = new ReadableStream({
    start(controller) {
      controller.enqueue(encoder.encode(toSseMessage("session", sessionId)));
      for (const token of tokenizeReply(reply)) {
        controller.enqueue(
          encoder.encode(toSseMessage("chunk", JSON.stringify(token))),
        );
      }
      controller.enqueue(encoder.encode(toSseMessage("done", "[DONE]")));
      controller.close();
    },
  });

  return new Response(stream, {
    headers: {
      "Content-Type": "text/event-stream",
      "Cache-Control": "no-cache, no-transform",
      Connection: "keep-alive",
    },
  });
}