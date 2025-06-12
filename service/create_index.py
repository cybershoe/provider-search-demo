from pymongo import MongoClient
from json import dumps, load
from sys import stdin
from time import sleep
from os import getenv

uri = getenv("MONGODB_URI", "mongodb://localhost:27017/")

# Create a new client and connect to the server
client = MongoClient(uri)

db = client[getenv('MONGODB_DBNAME', 'providerDB')]
collection = db[getenv('MONGODB_COLLECTION', 'providers')]

index = load(stdin)

collection.create_search_index(index)

print("Creating search index...", end='')

run = True
while run:
  try:
    res = collection.list_search_indexes().to_list()[0]['status']
    if res == "READY":
      print(" done!")
      run = False
    else:
      print('.', end='')
      sleep(10)
  except KeyboardInterrupt:
    run = False