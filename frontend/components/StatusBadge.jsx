"use client";

export default function StatusBadge({ status }) {
  return <span className={`ops-status ${status}`}>{status}</span>;
}
