import { NextResponse } from "next/server";
import { createSession, listSessions, normalizeUserId } from "../../../lib/server/sessionStore";

export async function GET(request) {
  const { searchParams } = new URL(request.url);
  const userId = normalizeUserId(searchParams.get("user_id"));
  const sessions = await listSessions(userId);
  return NextResponse.json(sessions);
}

export async function POST(request) {
  const payload = await request.json();
  const userId = normalizeUserId(payload.user_id);
  const session = await createSession(userId, payload.title || "New conversation", {
    user_name: payload.user_name,
    user_email: payload.user_email
  });

  return NextResponse.json({
    session_id: session.session_id,
    message: "Session created.",
    title: session.title
  });
}
