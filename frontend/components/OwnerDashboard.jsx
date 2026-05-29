"use client";

import { useEffect, useMemo, useState } from "react";
import { fetchJson } from "../lib/api";
import DashboardHeader from "./DashboardHeader";
import MetricCard from "./MetricCard";
import AlertMessage from "./AlertMessage";
import PanelSection from "./PanelSection";
import OwnerUpdatesList from "./OwnerUpdatesList";
import ResortUpdateForm from "./ResortUpdateForm";

export default function OwnerDashboard() {
  const [updates, setUpdates] = useState([]);
  const [resorts, setResorts] = useState([]);
  const [loading, setLoading] = useState(true);
  const [status, setStatus] = useState("");
  const [error, setError] = useState("");
  const [ownerId, setOwnerId] = useState("");
  const [ownedResorts, setOwnedResorts] = useState([]);
  const [opsSession, setOpsSession] = useState(null);
  const [activeTab, setActiveTab] = useState("updates");

  async function loadData(activeOwnerId = ownerId.trim()) {
    setLoading(true);
    setError("");
    try {
      const updatePath = activeOwnerId
        ? `/resorts/updates?owner_id=${encodeURIComponent(activeOwnerId)}`
        : "/resorts/updates";
      const requests = [fetchJson(updatePath), fetchJson("/resorts")];
      if (activeOwnerId) {
        requests.push(
          fetchJson(`/owners/${encodeURIComponent(activeOwnerId)}/resorts`),
        );
      }
      const [updatesData, resortsData, ownerResortsData = []] =
        await Promise.all(requests);
      setUpdates(updatesData);
      setResorts(resortsData);
      setOwnedResorts(ownerResortsData);
    } catch (loadError) {
      setError(loadError.message || "Could not load owner workflow data.");
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    async function loadSessionAndData() {
      try {
        const sessionResponse = await fetch("/ops-auth/session", {
          cache: "no-store",
        });
        if (!sessionResponse.ok) {
          throw new Error("Owner login required.");
        }
        const session = await sessionResponse.json();
        setOpsSession(session);
        const sessionOwnerId = session?.owner_id || "";
        setOwnerId(sessionOwnerId);
        await loadData(sessionOwnerId);
      } catch (sessionError) {
        setError(sessionError.message || "Owner session is not available.");
        setLoading(false);
      }
    }

    loadSessionAndData();
  }, []);

  useEffect(() => {
    function handleKeyDown(e) {
      const activeEl = document.activeElement;
      if (
        activeEl &&
        (activeEl.tagName === "INPUT" ||
          activeEl.tagName === "TEXTAREA" ||
          activeEl.tagName === "SELECT" ||
          activeEl.isContentEditable)
      ) {
        return;
      }

      if (e.key.toLowerCase() === "r") {
        e.preventDefault();
        loadData(ownerId.trim());
      }
    }

    window.addEventListener("keydown", handleKeyDown);
    return () => window.removeEventListener("keydown", handleKeyDown);
  }, [ownerId]);

  async function handleLogout() {
    await fetch("/ops-auth/logout", { method: "POST" });
    window.location.href = "/owner/login";
  }

  async function handleSubmit(payload) {
    setStatus("");
    setError("");
    try {
      const update = await fetchJson("/resorts/updates", {
        method: "POST",
        body: JSON.stringify(payload),
      });
      setUpdates((current) => [update, ...current]);
      setOwnerId(payload.owner_id);
      setStatus(
        payload.request_type === "create"
          ? "New resort submitted for admin review."
          : "Update submitted for admin review.",
      );
    } catch (submitError) {
      setError(submitError.message || "Could not submit update.");
    }
  }

  const ownerOptions = useMemo(
    () =>
      Array.from(
        new Set(updates.map((update) => update.owner_id).filter(Boolean)),
      ),
    [updates],
  );
  const submissionStats = useMemo(
    () => ({
      pending: updates.filter((update) => update.status === "pending").length,
      approved: updates.filter((update) => update.status === "approved").length,
      rejected: updates.filter((update) => update.status === "rejected").length,
    }),
    [updates],
  );

  return (
    <div className="ops-shell">
      <aside className="ops-sidebar" aria-label="Owner navigation">
        <div className="ops-brand">
          <span className="ops-brand-mark">
            <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round">
              <path d="M12 2L2 7l10 5 10-5-10-5z"/>
              <path d="M2 17l10 5 10-5"/>
              <path d="M2 12l10 5 10-5"/>
            </svg>
          </span>
          <span>
            <strong>WayFind</strong>
            <small>Partner Console</small>
          </span>
        </div>
        <nav className="ops-sidebar-nav">
          <button 
            className={activeTab === "updates" ? "active" : ""}
            type="button"
            onClick={() => setActiveTab("updates")}
          >
            <svg xmlns="http://www.w3.org/2000/svg" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
              <path d="M11 4H4a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2v-7"/>
              <path d="M18.5 2.5a2.121 2.121 0 1 1 3 3L12 15l-4 1 1-4 9.5-9.5z"/>
            </svg>
            Listing updates
          </button>
          <button 
            className={activeTab === "history" ? "active" : ""}
            type="button"
            onClick={() => setActiveTab("history")}
          >
            <svg xmlns="http://www.w3.org/2000/svg" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
              <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/>
              <polyline points="14 2 14 8 20 8"/>
              <line x1="16" y1="13" x2="8" y2="13"/>
              <line x1="16" y1="17" x2="8" y2="17"/>
              <polyline points="10 9 9 9 8 9"/>
            </svg>
            Review history
          </button>
          <button 
            className={activeTab === "published" ? "active" : ""}
            type="button"
            onClick={() => setActiveTab("published")}
          >
            <svg xmlns="http://www.w3.org/2000/svg" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
              <path d="M3 21h18"/>
              <path d="M9 21V9a3 3 0 0 0-6 0v12"/>
              <path d="M15 21V5a3 3 0 0 0-6 0v16"/>
              <path d="M21 21V11a3 3 0 0 0-6 0v10"/>
            </svg>
            Published resorts
          </button>
        </nav>
        <div className="ops-sidebar-note">
          <span>Signed in</span>
          <strong>{opsSession?.username || "Owner"}</strong>
        </div>
        <button
          className="ops-button secondary slim"
          type="button"
          onClick={handleLogout}
          style={{ width: "100%", justifyContent: "flex-start" }}
        >
          <svg xmlns="http://www.w3.org/2000/svg" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
            <path d="M9 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h4"/>
            <polyline points="16 17 21 12 16 7"/>
            <line x1="21" y1="12" x2="9" y2="12"/>
          </svg>
          Sign out
        </button>
      </aside>

      <main className="ops-main">
        <DashboardHeader
          kicker="Partner workspace"
          title="Manage resort information"
          subtitle="Submit listing changes, track review status, and keep your published resort details accurate."
          action={
            <button
              className="ops-button secondary"
              type="button"
              onClick={() => loadData()}
            >
              <svg 
                style={loading ? { animation: "ops-spin 1s linear infinite" } : {}} 
                xmlns="http://www.w3.org/2000/svg" 
                width="14" 
                height="14" 
                viewBox="0 0 24 24" 
                fill="none" 
                stroke="currentColor" 
                strokeWidth="2" 
                strokeLinecap="round" 
                strokeLinejoin="round"
              >
                <path d="M21.5 2v6h-6M21.34 15.57a10 10 0 1 1-.57-8.38l5.67-5.67"/>
              </svg>
              Refresh <kbd>R</kbd>
            </button>
          }
        />

        <section className="ops-metrics" aria-label="Owner summary">
          <MetricCard
            icon="🏨"
            label="Owned resorts"
            value={ownedResorts.length}
            description="Editable listings"
            variant="neutral"
          />
          <MetricCard
            icon="⏳"
            label="Pending review"
            value={submissionStats.pending}
            description="Awaiting approval"
            variant="warning"
          />
          <MetricCard
            icon="✓"
            label="Approved"
            value={submissionStats.approved}
            description="Accepted changes"
            variant="success"
          />
          <MetricCard
            icon="🌐"
            label="Public listings"
            value={resorts.length}
            description="Available records"
            variant="info"
          />
        </section>

        <AlertMessage type="success" message={status} icon="✓" />
        <AlertMessage type="error" message={error} icon="⚠" />

        {activeTab === "updates" && (
          <section className="ops-layout">
            <div className="ops-stack">
              <PanelSection
                kicker="Account Settings"
                title="Owner profile"
                className="compact"
              >
                <label className="ops-field">
                  <span>Owner ID</span>
                  <input
                    list="owner-options"
                    value={ownerId}
                    onChange={(event) => {
                      if (!opsSession?.owner_id) {
                        setOwnerId(event.target.value);
                      }
                    }}
                    onBlur={(event) => {
                      if (!opsSession?.owner_id) {
                        loadData(event.currentTarget.value.trim());
                      }
                    }}
                    placeholder="owner-001"
                    readOnly={Boolean(opsSession?.owner_id)}
                  />
                  <datalist id="owner-options">
                    {ownerOptions.map((knownOwnerId) => (
                      <option value={knownOwnerId} key={knownOwnerId} />
                    ))}
                  </datalist>
                </label>
                <p className="ops-muted" style={{ marginTop: "10px" }}>
                  Signed in as <strong>{opsSession?.username || "owner"}</strong>.
                  Your listing access is linked to this account.
                </p>
              </PanelSection>

              <ResortUpdateForm
                onSubmit={handleSubmit}
                ownerId={ownerId}
                ownedResorts={ownedResorts}
              />
            </div>

            <div className="ops-stack">
              <PanelSection
                kicker="Your Listings"
                title="Editable resorts"
                count={ownedResorts.length}
              >
                {ownedResorts.length ? (
                  <div className="ops-resort-grid">
                    {ownedResorts.map((resort) => (
                      <div className="ops-resort" key={resort.id}>
                        <strong>#{resort.id}</strong>
                        <span>{resort.name}</span>
                      </div>
                    ))}
                  </div>
                ) : (
                  <div className="ops-empty">
                    <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round" style={{ marginBottom: "8px", color: "var(--ops-text-tertiary)" }}>
                      <path d="M3 21h18"/>
                      <path d="M9 21V9a3 3 0 0 0-6 0v12"/>
                      <path d="M15 21V5a3 3 0 0 0-6 0v16"/>
                      <path d="M21 21V11a3 3 0 0 0-6 0v10"/>
                    </svg>
                    <span>No approved resorts yet. Submit a new resort listing and wait for admin approval.</span>
                  </div>
                )}
              </PanelSection>
            </div>
          </section>
        )}

        {activeTab === "history" && (
          <div style={{ maxWidth: "1000px", margin: "0 auto" }}>
            <OwnerUpdatesList
              updates={updates}
              loading={loading}
              ownerId={ownerId.trim()}
            />
          </div>
        )}

        {activeTab === "published" && (
          <div style={{ maxWidth: "1000px", margin: "0 auto" }}>
            <PanelSection
              kicker="Reference"
              title="Published resorts"
              count={resorts.length}
            >
              {resorts.length ? (
                <div className="ops-resort-grid" style={{ gridTemplateColumns: "repeat(3, minmax(0, 1fr))" }}>
                  {resorts.map((resort) => (
                    <div className="ops-resort" key={resort.id}>
                      <strong>#{resort.id}</strong>
                      <span>{resort.name}</span>
                    </div>
                  ))}
                </div>
              ) : (
                <div className="ops-empty">
                  <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round" style={{ marginBottom: "8px", color: "var(--ops-text-tertiary)" }}>
                    <circle cx="12" cy="12" r="10"/>
                    <line x1="2" y1="12" x2="22" y2="12"/>
                    <path d="M12 2a15.3 15.3 0 0 1 4 10 15.3 15.3 0 0 1-4 10 15.3 15.3 0 0 1-4-10 15.3 15.3 0 0 1 4-10z"/>
                  </svg>
                  <span>No public resort listings available.</span>
                </div>
              )}
            </PanelSection>
          </div>
        )}
      </main>
    </div>
  );
}
