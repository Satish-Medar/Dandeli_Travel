/* Protects operations pages and sensitive resort-management API paths. */
/* File: frontend/middleware.js */

import { NextResponse } from "next/server";

const COOKIE_NAME = "wayfind_ops_session";
const SECRET = process.env.OPS_AUTH_SECRET || "dev-change-this-wayfind-ops-secret";

function base64UrlToBytes(value) {
  const padded = value.replace(/-/g, "+").replace(/_/g, "/").padEnd(Math.ceil(value.length / 4) * 4, "=");
  return Uint8Array.from(atob(padded), (char) => char.charCodeAt(0));
}

function bytesToHex(bytes) {
  return Array.from(new Uint8Array(bytes))
    .map((byte) => byte.toString(16).padStart(2, "0"))
    .join("");
}

async function hmac(value) {
  const encoder = new TextEncoder();
  const key = await crypto.subtle.importKey(
    "raw",
    encoder.encode(SECRET),
    { name: "HMAC", hash: "SHA-256" },
    false,
    ["sign"],
  );
  const signature = await crypto.subtle.sign("HMAC", key, encoder.encode(value));
  return bytesToHex(signature);
}

async function readSession(request) {
  const raw = request.cookies.get(COOKIE_NAME)?.value;
  if (!raw || !raw.includes(".")) {
    return null;
  }
  const [encodedPayload, signature] = raw.split(".");
  if ((await hmac(encodedPayload)) !== signature) {
    return null;
  }
  try {
    const payload = JSON.parse(new TextDecoder().decode(base64UrlToBytes(encodedPayload)));
    if (!payload.expires_at || payload.expires_at < Math.floor(Date.now() / 1000)) {
      return null;
    }
    return payload;
  } catch {
    return null;
  }
}

function redirectToLogin(request, loginPath) {
  const url = request.nextUrl.clone();
  url.pathname = loginPath;
  url.searchParams.set("from", request.nextUrl.pathname);
  return NextResponse.redirect(url);
}

export default async function middleware(request) {
  const pathname = request.nextUrl.pathname;
  const session = await readSession(request);

  if (pathname === "/admin" || pathname.startsWith("/admin/")) {
    if (pathname === "/admin/login") {
      return session?.role === "admin" ? NextResponse.redirect(new URL("/admin", request.url)) : NextResponse.next();
    }
    return session?.role === "admin" ? NextResponse.next() : redirectToLogin(request, "/admin/login");
  }

  if (pathname === "/owner" || pathname.startsWith("/owner/")) {
    if (pathname === "/owner/login") {
      return session?.role === "owner" ? NextResponse.redirect(new URL("/owner", request.url)) : NextResponse.next();
    }
    return session?.role === "owner" ? NextResponse.next() : redirectToLogin(request, "/owner/login");
  }

  if (pathname.startsWith("/api/resorts/updates")) {
    if (session?.role === "admin" || session?.role === "owner") {
      return NextResponse.next();
    }
    return NextResponse.json({ detail: "Operations login required." }, { status: 401 });
  }

  if (pathname.startsWith("/api/owners/")) {
    if (session?.role === "admin" || session?.role === "owner") {
      return NextResponse.next();
    }
    return NextResponse.json({ detail: "Owner login required." }, { status: 401 });
  }

  return NextResponse.next();
}

export const config = {
  matcher: [
    "/admin/:path*",
    "/owner/:path*",
    "/api/resorts/updates/:path*",
    "/api/owners/:path*",
  ],
};
