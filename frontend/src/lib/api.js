export async function fetchJson(path, options = {}) {
  const response = await fetch(path, {
    ...options,
    headers: {
      "Content-Type": "application/json",
      ...(options.headers || {})
    }
  });

  if (!response.ok) {
    const fallback = "Request failed.";
    let detail = fallback;
    try {
      const payload = await response.json();
      detail = payload.detail || fallback;
    } catch {
      detail = fallback;
    }
    throw new Error(detail);
  }

  return response.json();
}

export async function streamChat(body, { onSession, onChunk }) {
  const response = await fetch("/chat/stream", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(body)
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
