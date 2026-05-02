import { MongoClient } from "mongodb";

const mongoUri = process.env.MONGODB_URI;
const dbName = process.env.MONGODB_DB_NAME || "dandeli_travel";

let globalWithMongo = globalThis;

if (!globalWithMongo.__mongoClientPromise) {
  globalWithMongo.__mongoClientPromise = null;
}

export async function getMongoDb() {
  if (!mongoUri) {
    return null;
  }
  if (!globalWithMongo.__mongoClientPromise) {
    const client = new MongoClient(mongoUri);
    globalWithMongo.__mongoClientPromise = client.connect();
  }
  const client = await globalWithMongo.__mongoClientPromise;
  return client.db(dbName);
}
