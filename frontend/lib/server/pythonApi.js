function getPythonApiBaseUrl() {
  return (process.env.PYTHON_API_BASE_URL || "http://127.0.0.1:8000").replace(/\/$/, "");
}

export async function requestAssistantReply({ messages, message }) {
  const response = await fetch(`${getPythonApiBaseUrl()}/assistant/reply`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json"
    },
    body: JSON.stringify({ messages, message }),
    cache: "no-store"
  });

  if (!response.ok) {
    throw new Error("Assistant service is unavailable.");
  }

  const payload = await response.json();
  return payload.reply || "I could not produce a response right now.";
}
