const GUEST_USER_STORAGE_KEY = "collegeproject_guest_user_id";
const CLERK_SCRIPT_ID = "clerk-js-sdk";

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
      const existingScript = document.getElementById(CLERK_SCRIPT_ID);
      if (existingScript) {
        existingScript.addEventListener("load", resolve, { once: true });
        existingScript.addEventListener("error", reject, { once: true });
        return;
      }

      const script = document.createElement("script");
      script.id = CLERK_SCRIPT_ID;
      script.src = "https://cdn.jsdelivr.net/npm/@clerk/clerk-js@latest/dist/clerk.browser.js";
      script.async = true;
      script.crossOrigin = "anonymous";
      script.setAttribute("data-clerk-publishable-key", publishableKey);
      script.onload = resolve;
      script.onerror = reject;
      document.body.appendChild(script);
    });
  }

  const clerkGlobal = window.Clerk;
  if (!clerkGlobal) {
    return null;
  }

  if (typeof clerkGlobal.load === "function") {
    await clerkGlobal.load({
      publishableKey
    });
    return clerkGlobal;
  }

  if (typeof clerkGlobal === "function") {
    const clerk = new clerkGlobal(publishableKey);
    await clerk.load();
    return clerk;
  }

  return null;
}
