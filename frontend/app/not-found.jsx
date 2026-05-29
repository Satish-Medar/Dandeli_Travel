import Link from "next/link";

export default function NotFoundPage() {
  return (
    <main className="app-not-found-shell">
      <div className="app-not-found-card">
        <div className="app-not-found-eyebrow">404</div>
        <h1 className="app-not-found-title">Page not found</h1>
        <p className="app-not-found-copy">
          The page you’re looking for doesn’t exist or has been moved. Head back
          to the WayFind homepage and continue exploring travel workflows.
        </p>
        <div className="app-not-found-actions">
          <Link href="/" className="ops-button primary">
            Return home
          </Link>
          <Link href="/chat" className="ops-button secondary">
            Open chat assistant
          </Link>
        </div>
        <p className="app-not-found-meta">
          Or double-check the URL for typos if you typed it directly.
        </p>
      </div>
    </main>
  );
}
