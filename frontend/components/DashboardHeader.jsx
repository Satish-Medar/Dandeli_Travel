"use client";

export default function DashboardHeader({ kicker, title, subtitle, action }) {
  return (
    <div className="ops-header">
      <div>
        {kicker && (
          <div style={{ display: "flex", alignItems: "center", gap: "8px", marginBottom: "4px" }}>
            <p className="ops-kicker" style={{ margin: 0 }}>{kicker}</p>
            <span style={{
              width: "6px",
              height: "6px",
              borderRadius: "50%",
              backgroundColor: "var(--ops-success)",
              display: "inline-block",
              boxShadow: "0 0 6px var(--ops-success)"
            }}></span>
          </div>
        )}
        <h1>{title}</h1>
        {subtitle && <p className="ops-subtitle">{subtitle}</p>}
      </div>
      {action && <div>{action}</div>}
    </div>
  );
}

