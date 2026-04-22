import { MongoClient } from "mongodb";

const mongoUri = process.env.MONGODB_URI;
const dbName = process.env.MONGODB_DB_NAME || "dandeli_travel";

let globalWithMongo = globalThis;

if (mongoUri && !globalWithMongo.__mongoClientPromise) {
  const client = new MongoClient(mongoUri);
  globalWithMongo.__mongoClientPromise = client.connect();
}

export async function getMongoDb() {
  if (!mongoUri) {
    return null;
  }
  const client = await globalWithMongo.__mongoClientPromise;
  return client.db(dbName);
}
