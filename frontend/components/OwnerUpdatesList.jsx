"use client";

import StatusBadge from "./StatusBadge";
import PanelSection from "./PanelSection";

function formatValue(value) {
  if (value === null || value === undefined || value === "") {
    return "-";
  }
  if (typeof value === "object") {
    return JSON.stringify(value);
  }
  return String(value);
}

export default function OwnerUpdatesList({
  updates = [],
  loading = false,
  ownerId = "",
}) {
  const visibleUpdates = ownerId
    ? updates.filter((update) => update.owner_id === ownerId)
    : updates;

  return (
    <PanelSection
      kicker="Activity Timeline"
      title="Review history"
      count={visibleUpdates.length}
    >
      {loading ? (
        <div className="ops-empty">
          <svg className="ops-spin" xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" style={{ marginBottom: "8px", color: "var(--ops-primary)" }}>
            <path d="M21.5 2v6h-6M21.34 15.57a10 10 0 1 1-.57-8.38l5.67-5.67"/>
          </svg>
          <span>Loading review history...</span>
        </div>
      ) : visibleUpdates.length ? (
        <div className="ops-timeline">
          {visibleUpdates.map((update) => (
            <div className={`ops-timeline-node ${update.status}`} key={update.id}>
              <div className="ops-timeline-marker"></div>
              <div className="ops-timeline-card">
                <div className="ops-timeline-header">
                  <h3 className="ops-timeline-title">
                    {update.request_type === "create"
                      ? "New resort listing"
                      : `Resort #${update.resort_id}`}
                  </h3>
                  <div className="ops-timeline-meta">
                    <span className="ops-timeline-time">
                      {formatValue(update.submitted_at)}
                    </span>
                    <StatusBadge status={update.status} />
                  </div>
                </div>

                {Object.keys(update.changes || {}).length > 0 && (
                  <dl className="ops-change-list">
                    {Object.entries(update.changes || {}).map(([key, value]) => (
                      <div key={key}>
                        <dt>{key.replaceAll("_", " ")}</dt>
                        <dd>{formatValue(value)}</dd>
                      </div>
                    ))}
                  </dl>
                )}

                {update.review_notes ? (
                  <div className="ops-review-note" style={{ display: "flex", alignItems: "flex-start", gap: "8px", marginTop: "10px" }}>
                    <svg xmlns="http://www.w3.org/2000/svg" width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" style={{ marginTop: "2px", flexShrink: 0, color: "var(--ops-accent)" }}>
                      <path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"/>
                    </svg>
                    <span style={{ fontSize: "0.775rem" }}>{update.review_notes}</span>
                  </div>
                ) : null}
              </div>
            </div>
          ))}
        </div>
      ) : (
        <div className="ops-empty">
          <svg xmlns="http://www.w3.org/2000/svg" width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round" style={{ marginBottom: "8px", color: "var(--ops-text-tertiary)" }}>
            <circle cx="12" cy="12" r="10"/>
            <polyline points="12 6 12 12 16 14"/>
          </svg>
          <span>No submission activity yet. Submit your first listing update to get started.</span>
        </div>
      )}
    </PanelSection>
  );
}
