/* Admin-only endpoint for creating owner login accounts. */
/* File: frontend/app/ops-auth/owners/route.js */

import { cookies } from "next/headers";
import { NextResponse } from "next/server";
import {
  createOrUpdateOwnerAccount,
  getOpsCookieName,
  readOpsSessionFromCookie,
} from "../../../lib/server/opsAuth";

export const runtime = "nodejs";

async function requireAdminSession() {
  const cookieStore = await cookies();
  const session = readOpsSessionFromCookie(cookieStore.get(getOpsCookieName())?.value);
  return session?.role === "admin" ? session : null;
}

export async function POST(request) {
  const session = await requireAdminSession();
  if (!session) {
    return NextResponse.json({ message: "Admin login required." }, { status: 401 });
  }

  try {
    const payload = await request.json();
    const account = await createOrUpdateOwnerAccount({
      username: payload.username,
      password: payload.password,
      ownerId: payload.owner_id,
      resortIds: payload.resort_ids,
    });
    return NextResponse.json({ account });
  } catch (error) {
    return NextResponse.json(
      { message: error.message || "Could not create owner account." },
      { status: 400 },
    );
  }
}
