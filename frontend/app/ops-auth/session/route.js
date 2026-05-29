/* Current operations session endpoint. */
/* File: frontend/app/ops-auth/session/route.js */

import { cookies } from "next/headers";
import { NextResponse } from "next/server";
import { getOpsCookieName, readOpsSessionFromCookie } from "../../../lib/server/opsAuth";

export const runtime = "nodejs";

export async function GET() {
  const cookieStore = await cookies();
  const session = readOpsSessionFromCookie(cookieStore.get(getOpsCookieName())?.value);
  if (!session) {
    return NextResponse.json({ authenticated: false }, { status: 401 });
  }
  return NextResponse.json({
    authenticated: true,
    role: session.role,
    username: session.username,
    owner_id: session.owner_id,
    resort_ids: session.resort_ids || [],
  });
}
