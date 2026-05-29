/* Logout endpoint for operations consoles. */
/* File: frontend/app/ops-auth/logout/route.js */

import { NextResponse } from "next/server";
import { clearOpsCookie } from "../../../lib/server/opsAuth";

export const runtime = "nodejs";

export async function POST() {
  const response = NextResponse.json({ ok: true });
  clearOpsCookie(response);
  return response;
}
