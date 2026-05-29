"use client";

export default function PanelSection({
  kicker,
  title,
  count,
  children,
  className = "",
}) {
  return (
    <div className={`ops-panel ${className}`}>
      <div className="ops-panel-head">
        <div>
          {kicker && <p className="ops-kicker">{kicker}</p>}
          {title && <h2>{title}</h2>}
        </div>
        {count !== undefined && <span className="ops-count">{count}</span>}
      </div>
      {children}
    </div>
  );
}
