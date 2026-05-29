"use client";

import { useState } from "react";

export default function OpsLogin({ role = "owner" }) {
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [pending, setPending] = useState(false);
  const isAdmin = role === "admin";

  async function handleSubmit(event) {
    event.preventDefault();
    setPending(true);
    setError("");
    try {
      const response = await fetch("/ops-auth/login", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ role, username, password }),
      });
      const payload = await response.json().catch(() => ({}));
      if (!response.ok) {
        throw new Error(payload.message || "Could not sign in.");
      }
      window.location.href =
        payload.redirect_to || (isAdmin ? "/admin" : "/owner");
    } catch (loginError) {
      setError(loginError.message || "Could not sign in.");
    } finally {
      setPending(false);
    }
  }

  return (
    <main className="ops-login-shell">
      <div className="ops-login-grid">
        <aside className="ops-login-panel">
          <div className="ops-brand ops-brand-lockup">
            <div className="ops-brand-mark">W</div>
            <div className="ops-brand-stack">
              <div className="ops-brand-name">
               <span> WayFind</span>
              </div>
              <div className="ops-brand-note">Travel operations</div>
            </div>
          </div>

          <div className="ops-login-panel-copy">
            <p className="ops-kicker admin">Restricted access</p>
            <h1>Secure admin access</h1>
            <p className="ops-login-panel-text">
              Access the operational console for resort content review, workflow
              controls, and secure administration.
            </p>
          </div>

          <div className="ops-login-panel-features">
            <div>
              <strong>Enterprise-grade security</strong>
              <p>
                Managed access for admin roles with auditing and content
                control.
              </p>
            </div>
            <div>
              <strong>Trust & control</strong>
              <p>
                Review updates, approve resorts, and keep the travel experience
                consistent.
              </p>
            </div>
            <div>
              <strong>Operational focus</strong>
              <p>
                A clean, focused admin entry point built for productivity and
                clarity.
              </p>
            </div>
          </div>
        </aside>

        <section
          className="ops-login-card"
          aria-labelledby="admin-login-heading"
        >
          <div className="ops-login-card-header">
            <div>
              <p className="ops-kicker admin">Admin authentication</p>
              <h2 id="admin-login-heading">Welcome back</h2>
            </div>
            <div className="ops-login-chip">Admin</div>
          </div>

          <p className="ops-login-card-intro">
            Sign in with the credentials issued for resort content review and
            operational management.
          </p>

          {error ? <div className="ops-alert error login">{error}</div> : null}

          <form className="ops-login-form" onSubmit={handleSubmit}>
            <label className="ops-field">
              <span>Username</span>
              <input
                value={username}
                onChange={(event) => setUsername(event.target.value)}
                autoComplete="username"
                placeholder={isAdmin ? "admin username" : "owner username"}
                required
              />
            </label>
            <label className="ops-field">
              <span>Password</span>
              <input
                value={password}
                onChange={(event) => setPassword(event.target.value)}
                autoComplete="current-password"
                placeholder="Password"
                type="password"
                required
              />
            </label>
            <button
              className="ops-button primary"
              type="submit"
              disabled={pending}
            >
              {pending ? "Signing in..." : "Sign in"}
            </button>
          </form>

          <p className="ops-login-footnote">
            Unauthorized access is monitored and restricted. Use your assigned
            admin credentials only.
          </p>
        </section>
      </div>
    </main>
  );
}
