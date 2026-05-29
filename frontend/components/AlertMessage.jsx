"use client";

export default function AlertMessage({ type, message, icon }) {
  if (!message) return null;

  return (
    <div className={`ops-alert ${type}`} role="alert">
      {icon && <span>{icon}</span>}
      <span>{message}</span>
    </div>
  );
}
