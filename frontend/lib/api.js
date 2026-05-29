/*
  Client-side API helper functions for the frontend.

  Simple overview:
  - `fetchJson` performs JSON requests to the backend.
  - `streamChat` handles server-sent event streaming for chat replies.
  - `toApiUrl` ensures requests go to the correct local API path.
*/
/* File: frontend/lib/api.js */

function toApiUrl(path) {
  if (path.startsWith("/api/")) {
    return path;
  }
  return `/api${path}`;
}

async function fetchWithTimeout(url, options = {}, timeoutMs = 20000) {
  const controller = new AbortController();
  const timeoutId = setTimeout(() => controller.abort(), timeoutMs);

  try {
    return await fetch(url, {
      signal: controller.signal,
      ...options,
    });
  } catch (error) {
    if (error.name === "AbortError") {
      throw new Error("Request timed out. The backend may not be running.");
    }
    throw error;
  } finally {
    clearTimeout(timeoutId);
  }
}

export async function fetchJson(path, options = {}) {
  const method = (options.method || "GET").toUpperCase();
  const headers = {
    ...(options.headers || {}),
  };

  if (options.body || (method !== "GET" && method !== "HEAD")) {
    headers["Content-Type"] = "application/json";
  }

  const response = await fetchWithTimeout(toApiUrl(path), {
    ...options,
    headers,
  });

  if (!response.ok) {
    const fallback = `Request failed with status ${response.status} ${response.statusText}.`;
    let detail = fallback;
    try {
      const payload = await response.json();
      detail = payload.detail || payload.message || fallback;
    } catch {
      try {
        const text = await response.text();
        detail = text ? `${fallback} ${text}` : fallback;
      } catch {
        detail = fallback;
      }
    }
    throw new Error(detail);
  }

  if (response.status === 204) {
    return null;
  }

  return response.json();
}

// Send a streamed chat request and invoke callbacks for session and tokens.
export async function streamChat(body, { onSession, onChunk }) {
  const response = await fetchWithTimeout(toApiUrl("/chat/stream"), {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(body),
  });

  if (!response.ok || !response.body) {
    throw new Error("The assistant could not respond right now.");
  }

  const reader = response.body.getReader();
  const decoder = new TextDecoder();
  let buffer = "";
  let reply = "";

  while (true) {
    const { value, done } = await reader.read();
    if (done) {
      break;
    }

    buffer += decoder.decode(value, { stream: true });
    const events = buffer.split("\n\n");
    buffer = events.pop() || "";

    for (const rawEvent of events) {
      const lines = rawEvent.split("\n");
      let eventName = "message";
      let data = "";

      for (const line of lines) {
        if (line.startsWith("event:")) {
          eventName = line.slice(6).trim();
        } else if (line.startsWith("data:")) {
          data += line.slice(5);
        }
      }

      if (eventName === "session") {
        onSession?.(data.trim());
      } else if (eventName === "chunk") {
        const token = JSON.parse(data);
        reply += token;
        onChunk?.(reply);
      } else if (eventName === "done") {
        return reply;
      }
    }
  }

  return reply;
}
