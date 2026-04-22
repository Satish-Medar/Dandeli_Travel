import { getOrCreateSession, normalizeUserId, recordMessage, saveSession } from "../../../../lib/server/sessionStore";
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
    user_email: payload.user_email
  };

  const [sessionId, session] = await getOrCreateSession(
    userId,
    payload.session_id || null,
    "New conversation",
    profile
  );

  const withUserMessage = recordMessage(session, "user", `${payload.message || ""}`.trim());

  let reply;
  try {
    reply = await requestAssistantReply({
      messages: withUserMessage.messages.slice(0, -1).map(({ role, content }) => ({ role, content })),
      message: payload.message
    });
  } catch {
    reply = "I'm having trouble reaching one of the AI services right now. Please try again in a moment.";
  }

  const finalSession = recordMessage(withUserMessage, "assistant", reply);
  await saveSession(userId, sessionId, finalSession, profile);

  const encoder = new TextEncoder();
  const stream = new ReadableStream({
    start(controller) {
      controller.enqueue(encoder.encode(toSseMessage("session", sessionId)));
      for (const token of tokenizeReply(reply)) {
        controller.enqueue(encoder.encode(toSseMessage("chunk", JSON.stringify(token))));
      }
      controller.enqueue(encoder.encode(toSseMessage("done", "[DONE]")));
      controller.close();
    }
  });

  return new Response(stream, {
    headers: {
      "Content-Type": "text/event-stream",
      "Cache-Control": "no-cache, no-transform",
      Connection: "keep-alive"
    }
  });
}
