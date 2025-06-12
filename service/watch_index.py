from os import getenv
from pymongo import MongoClient
from json import dumps
from time import sleep



uri = getenv("MONGODB_URI", "mongodb://localhost:27017/")
# Create a new client and connect to the server
with MongoClient(
    uri,
    tls=True,
    tlsCertificateKeyFile="keys/X509-cert-4247274353405106559.pem",
    authMechanism="MONGODB-X509"
    ) as client:

  db = client['Generator']
  collection = db['providers']
  run = True
  while run:
    try:
      res = collection.list_search_indexes().to_list()[0]['status']
      print(dumps(res))
      sleep(10)
    except KeyboardInterrupt:
      run = False
