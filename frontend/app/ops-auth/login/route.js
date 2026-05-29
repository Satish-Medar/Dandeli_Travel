/* Login endpoint for admin and owner operations consoles. */
/* File: frontend/app/ops-auth/login/route.js */

import { NextResponse } from "next/server";
import { createOpsSession, setOpsCookie, verifyOpsCredentials } from "../../../lib/server/opsAuth";

export const runtime = "nodejs";

function redirectPathForRole(role) {
  return role === "admin" ? "/admin" : "/owner";
}

export async function POST(request) {
  const payload = await request.json();
  const verified = await verifyOpsCredentials(payload);

  if (!verified) {
    return NextResponse.json({ message: "Invalid username or password." }, { status: 401 });
  }

  const response = NextResponse.json({
    role: verified.role,
    redirect_to: redirectPathForRole(verified.role),
  });
  setOpsCookie(response, createOpsSession(verified));
  return response;
}
