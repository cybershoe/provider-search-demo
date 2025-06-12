from pymongo import MongoClient
from json import load
from os import getenv
from itertools import islice
from sys import stdin

chunk_size = 1000

uri = getenv("MONGODB_URI", "mongodb://localhost:27017/")

# Create a new client and connect to the server
client = MongoClient(uri)

db = client[getenv('MONGODB_DBNAME', 'providerDB')]
collection = db[getenv('MONGODB_COLLECTION', 'providers')]

providers = load(stdin)
it = iter(providers)

processed = 0

for i in [list(islice(it, chunk_size)) for _ in range((len(providers) + chunk_size - 1) // chunk_size)]:
  print(f"Inserting records {processed+1:,d} to {processed+len(i):,d}")
  collection.insert_many(i)
  processed += len(i)
  
print (f"Inserted {processed:,d} records into {getenv('MONGODB_DBNAME', 'providerDB')}.{getenv('MONGODB_COLLECTION', 'providers')}")