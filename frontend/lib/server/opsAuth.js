/* Server-side authentication helpers for admin and owner operations pages. */
/* File: frontend/lib/server/opsAuth.js */

import crypto from "crypto";
import fs from "fs/promises";
import path from "path";

const COOKIE_NAME = "wayfind_ops_session";
const SESSION_TTL_SECONDS = 60 * 60 * 8;
const SECRET =
  process.env.OPS_AUTH_SECRET || "dev-change-this-wayfind-ops-secret";
const ADMIN_USERNAME = process.env.OPS_ADMIN_USERNAME || "satish";
const ADMIN_PASSWORD_SALT =
  process.env.OPS_ADMIN_PASSWORD_SALT || "wayfind-admin-v1";
const ADMIN_PASSWORD_HASH =
  process.env.OPS_ADMIN_PASSWORD_HASH ||
  "c61e80521e949f1fbf40bf1f252cefd0e1395f4a8aa52dc26372bb706f766676";

function hashPassword(password, salt) {
  return crypto
    .pbkdf2Sync(String(password), String(salt), 120000, 32, "sha256")
    .toString("hex");
}

function timingSafeEqualText(a, b) {
  const left = Buffer.from(String(a));
  const right = Buffer.from(String(b));
  return left.length === right.length && crypto.timingSafeEqual(left, right);
}

function signPayload(payload) {
  return crypto.createHmac("sha256", SECRET).update(payload).digest("hex");
}

export function createOpsSession({
  role,
  username,
  ownerId = "",
  resortIds = [],
}) {
  const payload = {
    role,
    username,
    owner_id: ownerId,
    resort_ids: resortIds,
    expires_at: Math.floor(Date.now() / 1000) + SESSION_TTL_SECONDS,
  };
  const encodedPayload = Buffer.from(JSON.stringify(payload), "utf8").toString(
    "base64url",
  );
  return `${encodedPayload}.${signPayload(encodedPayload)}`;
}

export function readOpsSessionFromCookie(cookieValue) {
  if (!cookieValue || !cookieValue.includes(".")) {
    return null;
  }
  const [encodedPayload, signature] = cookieValue.split(".");
  if (!timingSafeEqualText(signature, signPayload(encodedPayload))) {
    return null;
  }
  try {
    const payload = JSON.parse(
      Buffer.from(encodedPayload, "base64url").toString("utf8"),
    );
    if (
      !payload.expires_at ||
      payload.expires_at < Math.floor(Date.now() / 1000)
    ) {
      return null;
    }
    return payload;
  } catch {
    return null;
  }
}

export function setOpsCookie(response, sessionValue) {
  response.cookies.set({
    name: COOKIE_NAME,
    value: sessionValue,
    httpOnly: true,
    sameSite: "lax",
    secure: process.env.NODE_ENV === "production",
    path: "/",
    maxAge: SESSION_TTL_SECONDS,
  });
}

export function clearOpsCookie(response) {
  response.cookies.set({
    name: COOKIE_NAME,
    value: "",
    httpOnly: true,
    sameSite: "lax",
    secure: process.env.NODE_ENV === "production",
    path: "/",
    maxAge: 0,
  });
}

export function getOpsCookieName() {
  return COOKIE_NAME;
}

async function loadOwnerAccounts() {
  const accountsPath = path.join(
    process.cwd(),
    "..",
    "data",
    "json_files",
    "owner_accounts.json",
  );
  try {
    const raw = await fs.readFile(accountsPath, "utf8");
    const parsed = JSON.parse(raw);
    return Array.isArray(parsed.owners) ? parsed.owners : [];
  } catch {
    return [];
  }
}

async function saveOwnerAccounts(owners) {
  const accountsPath = path.join(
    process.cwd(),
    "..",
    "data",
    "json_files",
    "owner_accounts.json",
  );
  const payload = {
    owners: Array.isArray(owners) ? owners : [],
  };
  await fs.writeFile(
    accountsPath,
    `${JSON.stringify(payload, null, 2)}\n`,
    "utf8",
  );
}

export async function createOrUpdateOwnerAccount({
  username,
  password,
  ownerId,
  resortIds = [],
}) {
  const cleanedUsername = String(username || "").trim();
  const cleanedOwnerId = String(ownerId || "").trim();
  const cleanedPassword = String(password || "");
  const cleanedResortIds = Array.isArray(resortIds)
    ? resortIds.map((value) => String(value).trim()).filter(Boolean)
    : String(resortIds || "")
        .split(",")
        .map((value) => value.trim())
        .filter(Boolean);

  if (!cleanedUsername || !cleanedOwnerId || !cleanedPassword) {
    throw new Error("Username, password, and owner ID are required.");
  }
  if (cleanedPassword.length < 8) {
    throw new Error("Password must be at least 8 characters.");
  }

  const owners = await loadOwnerAccounts();
  const salt = crypto.randomBytes(16).toString("hex");
  const nextAccount = {
    username: cleanedUsername,
    owner_id: cleanedOwnerId,
    resort_ids: cleanedResortIds,
    password_salt: salt,
    password_hash: hashPassword(cleanedPassword, salt),
    active: true,
    updated_at: new Date().toISOString(),
  };

  const existingIndex = owners.findIndex(
    (account) => account.username === cleanedUsername,
  );
  if (existingIndex >= 0) {
    owners[existingIndex] = {
      ...owners[existingIndex],
      ...nextAccount,
    };
  } else {
    owners.push({
      ...nextAccount,
      created_at: new Date().toISOString(),
    });
  }

  await saveOwnerAccounts(owners);
  return {
    username: nextAccount.username,
    owner_id: nextAccount.owner_id,
    resort_ids: nextAccount.resort_ids,
    active: nextAccount.active,
  };
}

export async function verifyOpsCredentials({ role, username, password }) {
  const cleanedRole = String(role || "")
    .trim()
    .toLowerCase();
  const cleanedUsername = String(username || "").trim();

  if (cleanedRole === "admin") {
    const candidateHash = hashPassword(password, ADMIN_PASSWORD_SALT);
    if (
      cleanedUsername === ADMIN_USERNAME &&
      timingSafeEqualText(candidateHash, ADMIN_PASSWORD_HASH)
    ) {
      return {
        role: "admin",
        username: cleanedUsername,
        ownerId: "",
        resortIds: [],
      };
    }
    return null;
  }

  if (cleanedRole === "owner") {
    const owners = await loadOwnerAccounts();
    const owner = owners.find(
      (account) =>
        account.username === cleanedUsername && account.active !== false,
    );
    if (!owner) {
      return null;
    }
    const candidateHash = hashPassword(password, owner.password_salt);
    if (!timingSafeEqualText(candidateHash, owner.password_hash)) {
      return null;
    }
    return {
      role: "owner",
      username: owner.username,
      ownerId: owner.owner_id,
      resortIds: owner.resort_ids || [],
    };
  }

  return null;
}
