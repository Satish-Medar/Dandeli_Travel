const GUEST_USER_STORAGE_KEY = "collegeproject_guest_user_id";

export function ensureGuestUserId() {
  let stored = window.localStorage.getItem(GUEST_USER_STORAGE_KEY);
  if (!stored) {
    stored = `guest-${crypto.randomUUID()}`;
    window.localStorage.setItem(GUEST_USER_STORAGE_KEY, stored);
  }
  return stored;
}

export function getCurrentUserId(clerkInstance) {
  if (clerkInstance?.user?.id) {
    return clerkInstance.user.id;
  }
  return ensureGuestUserId();
}

export async function loadClerkInstance(publishableKey) {
  if (!publishableKey) {
    return null;
  }

  if (!window.Clerk) {
    await new Promise((resolve, reject) => {
      const script = document.createElement("script");
      script.src = "https://cdn.jsdelivr.net/npm/@clerk/clerk-js@latest/dist/clerk.browser.js";
      script.async = true;
      script.onload = resolve;
      script.onerror = reject;
      document.body.appendChild(script);
    });
  }

  const ClerkCtor = window.Clerk;
  if (!ClerkCtor) {
    return null;
  }

  const clerk = new ClerkCtor(publishableKey);
  await clerk.load();
  return clerk;
}
