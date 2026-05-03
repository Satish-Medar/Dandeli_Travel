"use client";

import { useEffect, useMemo, useState } from "react";

function buildClerkHostedUrl(mode) {
  const publishableKey = process.env.NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY;
  if (!publishableKey || typeof window === "undefined") {
    return "";
  }

  const redirectUrl = window.location.origin;
  const base = mode === "signup" ? "sign-up" : "sign-in";
  const params = new URLSearchParams({
    redirect_url: redirectUrl,
    after_sign_in_url: redirectUrl,
    after_sign_up_url: redirectUrl
  });

  if (publishableKey.startsWith("pk_test_")) {
    try {
      const b64 = publishableKey.split("pk_test_")[1];
      const decoded = atob(b64);
      const host = decoded.replace("$", "");
      return `https://${host}/${base}?${params.toString()}`;
    } catch {
      // fallback
    }
  }

  params.set("publishable_key", publishableKey);
  return `https://accounts.clerk.com/${base}?${params.toString()}`;
}

export default function ClerkAuthPanel({ mode }) {
  const [error, setError] = useState("");

  const authUrl = useMemo(() => {
    if (typeof window === "undefined") {
      return "";
    }
    return buildClerkHostedUrl(mode);
  }, [mode]);

  useEffect(() => {
    if (!authUrl) {
      setError("Clerk publishable key is missing.");
      return;
    }

    const timeout = window.setTimeout(() => {
      window.location.href = authUrl;
    }, 150);

    return () => window.clearTimeout(timeout);
  }, [authUrl]);

  return (
    <div className="auth-page-shell">
      <div className="auth-page-card">
        <div className="auth-page-copy">
          <p className="kicker">Vana AI</p>
          <h1>{mode === "signup" ? "Create your account" : "Welcome back"}</h1>
          <p className="subtitle">
            {mode === "signup"
              ? "Redirecting you to Clerk sign up."
              : "Redirecting you to Clerk sign in."}
          </p>
        </div>

        {error ? <p className="auth-error">{error}</p> : null}
        {!error ? (
          <div className="auth-actions">
            <p className="auth-loading">Redirecting to secure authentication...</p>
            <a className="auth-link" href={authUrl}>
              Continue
            </a>
          </div>
        ) : null}
      </div>
    </div>
  );
}
