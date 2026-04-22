import { mkdir, readFile, writeFile } from "fs/promises";
import path from "path";

const STORE_PATH = path.join(process.cwd(), "..", "data", "json_files", "chat_sessions.json");

async function ensureStoreFile() {
  await mkdir(path.dirname(STORE_PATH), { recursive: true });
  try {
    await readFile(STORE_PATH, "utf8");
  } catch {
    await writeFile(STORE_PATH, "{}", "utf8");
  }
}

export async function loadFileStore() {
  await ensureStoreFile();
  const raw = await readFile(STORE_PATH, "utf8");
  return JSON.parse(raw || "{}");
}

export async function saveFileStore(store) {
  await ensureStoreFile();
  await writeFile(STORE_PATH, JSON.stringify(store, null, 2), "utf8");
}
