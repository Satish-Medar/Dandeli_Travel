import { NextResponse } from "next/server";

export async function GET() {
  const publishableKey =
    process.env.NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY ||
    process.env.CLERK_PUBLISHABLE_KEY ||
    null;

  return NextResponse.json({
    clerk_publishable_key: publishableKey,
    clerk_enabled: Boolean(publishableKey)
  });
}
