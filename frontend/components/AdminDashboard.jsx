"use client";

import { useEffect, useMemo, useState } from "react";
import { fetchJson } from "../lib/api";
import DashboardHeader from "./DashboardHeader";
import MetricCard from "./MetricCard";
import StatusBadge from "./StatusBadge";
import AlertMessage from "./AlertMessage";
import PanelSection from "./PanelSection";

function formatValue(value) {
  if (value === null || value === undefined || value === "") {
    return "-";
  }
  if (Array.isArray(value)) {
    return value.join(", ");
  }
  if (typeof value === "object") {
    return JSON.stringify(value, null, 2);
  }
  return String(value);
}

function buildDiffRows(diff) {
  const changes = diff?.changes || {};
  return Object.keys(changes).map((field) => ({
    field,
    before: diff?.before?.[field],
    after: diff?.after?.[field],
  }));
}

export default function AdminDashboard() {
  const [updates, setUpdates] = useState([]);
  const [selectedId, setSelectedId] = useState(null);
  const [diff, setDiff] = useState(null);
  const [reviewerId, setReviewerId] = useState("admin-001");
  const [reviewNotes, setReviewNotes] = useState("");
  const [statusFilter, setStatusFilter] = useState("pending");
  const [loading, setLoading] = useState(true);
  const [working, setWorking] = useState(false);
  const [error, setError] = useState("");
  const [notice, setNotice] = useState("");
  const [ownerAccount, setOwnerAccount] = useState({
    username: "",
    password: "",
    owner_id: "",
    resort_ids: "",
  });
  const [creatingOwner, setCreatingOwner] = useState(false);
  const [isProvisionDrawerOpen, setIsProvisionDrawerOpen] = useState(false);
  const [activeTab, setActiveTab] = useState("queue");
  const [resorts, setResorts] = useState([]);

  async function loadUpdates(nextStatus = statusFilter) {
    setLoading(true);
    setError("");
    try {
      const query =
        nextStatus === "all" ? "" : `?status=${encodeURIComponent(nextStatus)}`;
      const [data, resortsData] = await Promise.all([
        fetchJson(`/resorts/updates${query}`),
        fetchJson("/resorts").catch(() => []),
      ]);
      setUpdates(data);
      setResorts(resortsData);
      if (!data.some((update) => update.id === selectedId)) {
        setSelectedId(data[0]?.id || null);
      }
    } catch (loadError) {
      setError(loadError.message || "Could not load update queue.");
      setUpdates([]);
      setResorts([]);
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    loadUpdates(statusFilter);
  }, [statusFilter]);

  useEffect(() => {
    async function loadDiff() {
      if (!selectedId) {
        setDiff(null);
        return;
      }

      setError("");
      try {
        setDiff(await fetchJson(`/resorts/updates/${selectedId}/diff`));
      } catch (diffError) {
        setDiff(null);
        setError(diffError.message || "Could not load update diff.");
      }
    }

    loadDiff();
  }, [selectedId]);

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

      const key = e.key.toLowerCase();

      if (key === "r") {
        e.preventDefault();
        loadUpdates(statusFilter);
      }

      if (key === "c") {
        e.preventDefault();
        setIsProvisionDrawerOpen((prev) => !prev);
      }

      if (key === "j") {
        e.preventDefault();
        if (updates.length > 0) {
          const currentIndex = updates.findIndex((u) => u.id === selectedId);
          if (currentIndex < updates.length - 1) {
            setSelectedId(updates[currentIndex + 1].id);
          }
        }
      }

      if (key === "k") {
        e.preventDefault();
        if (updates.length > 0) {
          const currentIndex = updates.findIndex((u) => u.id === selectedId);
          if (currentIndex > 0) {
            setSelectedId(updates[currentIndex - 1].id);
          }
        }
      }

      if (key === "a") {
        const selectedUpdate = updates.find((u) => u.id === selectedId);
        if (selectedUpdate && selectedUpdate.status === "pending") {
          e.preventDefault();
          reviewUpdate("approve");
        }
      }

      if (key === "x") {
        const selectedUpdate = updates.find((u) => u.id === selectedId);
        if (selectedUpdate && selectedUpdate.status === "pending") {
          e.preventDefault();
          reviewUpdate("reject");
        }
      }
    }

    window.addEventListener("keydown", handleKeyDown);
    return () => {
      window.removeEventListener("keydown", handleKeyDown);
    };
  }, [updates, selectedId, statusFilter, reviewerId, reviewNotes]);

  async function reviewUpdate(action) {
    if (!selectedId || !reviewerId.trim()) {
      setError("Reviewer ID is required.");
      return;
    }

    setWorking(true);
    setError("");
    setNotice("");
    try {
      await fetchJson(`/resorts/updates/${selectedId}/${action}`, {
        method: "POST",
        body: JSON.stringify({
          reviewer_id: reviewerId.trim(),
          review_notes: reviewNotes.trim() || null,
        }),
      });
      setNotice(`Update ${action === "approve" ? "approved" : "rejected"}.`);
      setReviewNotes("");
      await loadUpdates(statusFilter);
    } catch (reviewError) {
      setError(reviewError.message || `Could not ${action} update.`);
    } finally {
      setWorking(false);
    }
  }

  const selectedUpdate = useMemo(
    () => updates.find((update) => update.id === selectedId) || null,
    [updates, selectedId],
  );
  const diffRows = buildDiffRows(diff);
  const queueStats = useMemo(
    () => ({
      pending: updates.filter((update) => update.status === "pending").length,
      approved: updates.filter((update) => update.status === "approved").length,
      rejected: updates.filter((update) => update.status === "rejected").length,
    }),
    [updates],
  );

  async function handleLogout() {
    await fetch("/ops-auth/logout", { method: "POST" });
    window.location.href = "/admin/login";
  }

  function updateOwnerAccountField(event) {
    const { name, value } = event.target;
    setOwnerAccount((current) => ({ ...current, [name]: value }));
  }

  async function createOwnerAccount(event) {
    event.preventDefault();
    setCreatingOwner(true);
    setError("");
    setNotice("");
    try {
      const response = await fetch("/ops-auth/owners", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          username: ownerAccount.username.trim(),
          password: ownerAccount.password,
          owner_id: ownerAccount.owner_id.trim(),
          resort_ids: ownerAccount.resort_ids
            .split(",")
            .map((value) => value.trim())
            .filter(Boolean),
        }),
      });
      const payload = await response.json().catch(() => ({}));
      if (!response.ok) {
        throw new Error(payload.message || "Could not create owner account.");
      }
      setNotice(`Owner login saved for ${payload.account.username}.`);
      setOwnerAccount({
        username: "",
        password: "",
        owner_id: "",
        resort_ids: "",
      });
    } catch (ownerError) {
      setError(ownerError.message || "Could not create owner account.");
    } finally {
      setCreatingOwner(false);
    }
  }

  return (
    <div className="ops-shell">
      <aside className="ops-sidebar" aria-label="Admin navigation">
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
            <small>Admin Console</small>
          </span>
        </div>
        <nav className="ops-sidebar-nav">
          <button 
            className={activeTab === "queue" ? "active" : ""}
            type="button"
            onClick={() => setActiveTab("queue")}
          >
            <svg xmlns="http://www.w3.org/2000/svg" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
              <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/>
              <polyline points="14 2 14 8 20 8"/>
              <line x1="16" y1="13" x2="8" y2="13"/>
              <line x1="16" y1="17" x2="8" y2="17"/>
              <polyline points="10 9 9 9 8 9"/>
            </svg>
            Review queue
          </button>
          <button 
            className={activeTab === "access" ? "active" : ""}
            type="button"
            onClick={() => setActiveTab("access")}
          >
            <svg xmlns="http://www.w3.org/2000/svg" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
              <path d="M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2"/>
              <circle cx="9" cy="7" r="4"/>
              <path d="M23 21v-2a4 4 0 0 0-3-3.87"/>
              <path d="M16 3.13a4 4 0 0 1 0 7.75"/>
            </svg>
            Owner access
          </button>
          <button 
            className={activeTab === "published" ? "active" : ""}
            type="button"
            onClick={() => setActiveTab("published")}
          >
            <svg xmlns="http://www.w3.org/2000/svg" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
              <line x1="18" y1="20" x2="18" y2="10"/>
              <line x1="12" y1="20" x2="12" y2="4"/>
              <line x1="6" y1="20" x2="6" y2="14"/>
            </svg>
            Published resorts
          </button>
        </nav>
        <div className="ops-sidebar-note">
          <span>Signed in</span>
          <strong>Administrator</strong>
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
          kicker="Content review"
          title="Resort update queue"
          subtitle="Check owner-submitted changes, compare proposed values, and publish only verified resort data."
          action={
            <button
              className="ops-button secondary"
              type="button"
              onClick={() => loadUpdates(statusFilter)}
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

        <section className="ops-metrics" aria-label="Review summary">
          <MetricCard
            icon="⏳"
            label="Pending queue"
            value={queueStats.pending}
            description="Awaiting decisions"
            variant="warning"
          />
          <MetricCard
            icon="✓"
            label="Approved"
            value={queueStats.approved}
            description="Published resort items"
            variant="success"
          />
          <MetricCard
            icon="×"
            label="Rejected"
            value={queueStats.rejected}
            description="Sent back to owner"
            variant="danger"
          />
          <MetricCard
            icon="🔍"
            label="Filter queue"
            value={statusFilter}
            description="Current workspace status"
            variant="neutral"
          />
        </section>

        <AlertMessage type="success" message={notice} icon="✓" />
        <AlertMessage type="error" message={error} icon="⚠" />

        {activeTab === "queue" && (
          <section className="ops-layout admin">
            <aside className="ops-panel ops-queue">
              <div className="ops-panel-head">
                <div>
                  <p className="ops-kicker">
                    Submission Queue <span style={{ textTransform: "lowercase", opacity: 0.8 }}>(nav <kbd>J</kbd> <kbd>K</kbd>)</span>
                  </p>
                  <h2>Queue: {statusFilter}</h2>
                </div>
                <span className="ops-count">{updates.length}</span>
              </div>

              <div className="ops-segmented">
                {["pending", "approved", "rejected", "all"].map((status) => (
                  <button
                    className={statusFilter === status ? "active" : ""}
                    key={status}
                    type="button"
                    onClick={() => setStatusFilter(status)}
                    style={{ textTransform: "capitalize" }}
                  >
                    {status}
                  </button>
                ))}
              </div>

              {loading ? (
                <div className="ops-empty">
                  <svg className="ops-spin" xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" style={{ marginBottom: "4px", color: "var(--ops-accent)" }}>
                    <path d="M21.5 2v6h-6M21.34 15.57a10 10 0 1 1-.57-8.38l5.67-5.67"/>
                  </svg>
                  <span>Loading submissions...</span>
                </div>
              ) : updates.length ? (
                <div className="ops-list">
                  {updates.map((update) => (
                    <button
                      className={`ops-queue-item ${selectedId === update.id ? "active" : ""}`}
                      key={update.id}
                      type="button"
                      onClick={() => setSelectedId(update.id)}
                    >
                      <div style={{ display: "flex", alignItems: "center", gap: "8px", width: "100%", minWidth: 0 }}>
                        <div style={{
                          width: "24px",
                          height: "24px",
                          borderRadius: "4px",
                          backgroundColor: update.request_type === "create" ? "var(--ops-success-light)" : "var(--ops-info-light)",
                          color: update.request_type === "create" ? "var(--ops-success)" : "var(--ops-info)",
                          display: "flex",
                          alignItems: "center",
                          justifyContent: "center",
                          flexShrink: 0,
                          fontSize: "0.8rem",
                          fontWeight: "600"
                        }}>
                          {update.request_type === "create" ? "+" : "✎"}
                        </div>
                        <span style={{ display: "flex", flexDirection: "column", gap: "1px", minWidth: 0, flex: 1 }}>
                          <strong style={{ fontSize: "0.775rem", textOverflow: "ellipsis", overflow: "hidden", whiteSpace: "nowrap" }}>
                            {update.request_type === "create"
                              ? "New resort listing"
                              : `Resort #${update.resort_id}`}
                          </strong>
                          <small style={{ fontSize: "0.65rem", color: "var(--ops-text-tertiary)" }}>by {update.owner_id}</small>
                        </span>
                        <StatusBadge status={update.status} />
                      </div>
                    </button>
                  ))}
                </div>
              ) : (
                <div className="ops-empty">
                  <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round" style={{ marginBottom: "4px", color: "var(--ops-text-tertiary)" }}>
                    <rect x="3" y="4" width="18" height="18" rx="2" ry="2"/>
                    <line x1="9" y1="9" x2="15" y2="9"/>
                    <line x1="9" y1="13" x2="15" y2="13"/>
                    <line x1="9" y1="17" x2="13" y2="17"/>
                  </svg>
                  <span>No submissions in queue</span>
                </div>
              )}
            </aside>

            <div className="ops-stack">
              <PanelSection
                kicker="Review Workspace"
                title={
                  selectedUpdate
                    ? selectedUpdate.request_type === "create"
                      ? "New listing request"
                      : `Resort #${selectedUpdate.resort_id}`
                    : "Select a submission"
                }
              >
                {selectedUpdate ? (
                  <>
                    <div className="ops-meta-grid">
                      <div>
                        <span>Type</span>
                        <strong style={{ textTransform: "uppercase", fontSize: "0.75rem", color: "var(--ops-accent)" }}>
                          {selectedUpdate.request_type || "update"}
                        </strong>
                      </div>
                      <div>
                        <span>Submission ID</span>
                        <strong>{selectedUpdate.id}</strong>
                      </div>
                      <div>
                        <span>Owner</span>
                        <strong>{selectedUpdate.owner_id}</strong>
                      </div>
                      <div>
                        <span>Submitted</span>
                        <strong>
                          {formatValue(selectedUpdate.submitted_at)}
                        </strong>
                      </div>
                    </div>

                    <div className="ops-diff-grid">
                      {diffRows.length ? (
                        diffRows.map((row) => {
                          const beforeVal = formatValue(row.before);
                          const afterVal = formatValue(row.after);
                          const isChanged = beforeVal !== afterVal;
                          return (
                            <div className="ops-diff-card" key={row.field}>
                              <div className="ops-diff-card-header">
                                <span className="ops-diff-card-title">
                                  {row.field.replaceAll("_", " ")}
                                </span>
                              </div>
                              <div className="ops-diff-split">
                                <div className={`ops-diff-pane ${isChanged ? "before" : "unchanged"}`}>
                                  {beforeVal}
                                </div>
                                <div className={`ops-diff-pane ${isChanged ? "after" : "unchanged"}`}>
                                  {afterVal}
                                </div>
                              </div>
                            </div>
                          );
                        })
                      ) : (
                        <div className="ops-empty">No changes to review.</div>
                      )}
                    </div>
                  </>
                ) : (
                  <div className="ops-empty">
                    <svg xmlns="http://www.w3.org/2000/svg" width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round" style={{ marginBottom: "8px", color: "var(--ops-text-tertiary)" }}>
                      <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/>
                      <polyline points="14 2 14 8 20 8"/>
                      <line x1="9" y1="15" x2="15" y2="15"/>
                      <line x1="12" y1="12" x2="12" y2="18"/>
                    </svg>
                    <span>Select a submission from the queue to review details.</span>
                  </div>
                )}
              </PanelSection>

              {selectedUpdate?.status === "pending" ? (
                <PanelSection
                  kicker="Review Action"
                  title="Approve or reject"
                  className="compact"
                >
                  <div className="ops-form-grid review">
                    <label className="ops-field">
                      <span>Reviewer ID</span>
                      <input
                        value={reviewerId}
                        onChange={(event) => setReviewerId(event.target.value)}
                        placeholder="admin-001"
                      />
                    </label>
                    <label className="ops-field">
                      <span>Review Notes</span>
                      <textarea
                        value={reviewNotes}
                        onChange={(event) => setReviewNotes(event.target.value)}
                        placeholder="Optional decision notes"
                      />
                    </label>
                  </div>
                  <div className="ops-actions">
                    <button
                      className="ops-button danger"
                      type="button"
                      disabled={working}
                      onClick={() => reviewUpdate("reject")}
                    >
                      <svg xmlns="http://www.w3.org/2000/svg" width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                        <circle cx="12" cy="12" r="10"/>
                        <line x1="4.93" y1="4.93" x2="19.07" y2="19.07"/>
                      </svg>
                      Reject <kbd>X</kbd>
                    </button>
                    <button
                      className="ops-button primary"
                      type="button"
                      disabled={working}
                      onClick={() => reviewUpdate("approve")}
                    >
                      <svg xmlns="http://www.w3.org/2000/svg" width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round">
                        <polyline points="20 6 9 17 4 12"/>
                      </svg>
                      Approve & Publish <kbd>A</kbd>
                    </button>
                  </div>
                </PanelSection>
              ) : null}
            </div>
          </section>
        )}

        {activeTab === "access" && (
          <div style={{ maxWidth: "800px", margin: "0 auto" }}>
            <PanelSection
              kicker="Access Control"
              title="Create owner login"
              className="compact ops-form-panel"
            >
              <form onSubmit={createOwnerAccount}>
                <div className="ops-form-grid">
                  <label className="ops-field">
                    <span>Username</span>
                    <input
                      name="username"
                      value={ownerAccount.username}
                      onChange={updateOwnerAccountField}
                      placeholder="sparow-owner"
                      autoComplete="off"
                      required
                    />
                  </label>
                  <label className="ops-field">
                    <span>Temporary Password</span>
                    <input
                      name="password"
                      value={ownerAccount.password}
                      onChange={updateOwnerAccountField}
                      placeholder="At least 8 characters"
                      type="password"
                      autoComplete="new-password"
                      required
                    />
                  </label>
                  <label className="ops-field">
                    <span>Owner ID</span>
                    <input
                      name="owner_id"
                      value={ownerAccount.owner_id}
                      onChange={updateOwnerAccountField}
                      placeholder="owner-sparow"
                      required
                    />
                  </label>
                  <label className="ops-field">
                    <span>Allowed Resort IDs</span>
                    <input
                      name="resort_ids"
                      value={ownerAccount.resort_ids}
                      onChange={updateOwnerAccountField}
                      placeholder="e.g., 83 or 12,18,25"
                    />
                  </label>
                </div>
                <div className="ops-actions">
                  <button
                    className="ops-button primary"
                    type="submit"
                    disabled={creatingOwner}
                  >
                    {creatingOwner ? "Saving..." : "Create login"}
                  </button>
                </div>
              </form>
            </PanelSection>
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
