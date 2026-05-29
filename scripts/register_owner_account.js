/* Register or update resort owner login credentials. */
/* File: scripts/register_owner_account.js */

const crypto = require("crypto");
const fs = require("fs");
const path = require("path");

function usage() {
  console.log(
    "Usage: node scripts/register_owner_account.js <username> <password> <owner_id> [resort_ids_csv]\n" +
      "Example: node scripts/register_owner_account.js owner-elephant StrongPass123 owner-001 1,5,9",
  );
}

const [, , username, password, ownerId, resortIdsCsv = ""] = process.argv;
if (!username || !password || !ownerId) {
  usage();
  process.exit(1);
}

const storePath = path.join(__dirname, "..", "data", "json_files", "owner_accounts.json");
const salt = crypto.randomBytes(16).toString("hex");
const passwordHash = crypto.pbkdf2Sync(password, salt, 120000, 32, "sha256").toString("hex");
const resortIds = resortIdsCsv
  .split(",")
  .map((value) => value.trim())
  .filter(Boolean);

const store = fs.existsSync(storePath)
  ? JSON.parse(fs.readFileSync(storePath, "utf8"))
  : { owners: [] };

store.owners = Array.isArray(store.owners) ? store.owners : [];
const nextAccount = {
  username,
  owner_id: ownerId,
  resort_ids: resortIds,
  password_salt: salt,
  password_hash: passwordHash,
  active: true,
  updated_at: new Date().toISOString(),
};

const existingIndex = store.owners.findIndex((account) => account.username === username);
if (existingIndex >= 0) {
  store.owners[existingIndex] = {
    ...store.owners[existingIndex],
    ...nextAccount,
  };
} else {
  store.owners.push({
    ...nextAccount,
    created_at: new Date().toISOString(),
  });
}

fs.writeFileSync(storePath, `${JSON.stringify(store, null, 2)}\n`);
console.log(`Owner account saved for ${username} (${ownerId}).`);
