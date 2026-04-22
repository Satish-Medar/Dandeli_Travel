import { NextResponse } from "next/server";
import { clearSession, getSession, normalizeUserId } from "../../../../lib/server/sessionStore";

export async function GET(request, context) {
  const { searchParams } = new URL(request.url);
  const userId = normalizeUserId(searchParams.get("user_id"));
  const { sessionId } = await context.params;
  const session = await getSession(userId, sessionId);

  if (!session) {
    return NextResponse.json({ detail: "Session not found." }, { status: 404 });
  }

  return NextResponse.json(session);
}

export async function DELETE(request, context) {
  const { searchParams } = new URL(request.url);
  const userId = normalizeUserId(searchParams.get("user_id"));
  const { sessionId } = await context.params;
  const session = await clearSession(userId, sessionId);

  if (!session) {
    return NextResponse.json({ detail: "Session not found." }, { status: 404 });
  }

  return NextResponse.json({
    session_id: sessionId,
    message: "Session cleared.",
    title: session.title
  });
}
