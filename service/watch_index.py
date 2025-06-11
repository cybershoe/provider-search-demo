from argparse import ArgumentParser
from faker import Faker
from sys import stdout
from random import choices, choice, randint
from pymongo import MongoClient
from json import load, dumps
from time import sleep



MONGO_URI = uri = "mongodb+srv://providerdb.bzepjj.mongodb.net/?authSource=%24external&authMechanism=MONGODB-X509&retryWrites=true&w=majority&appName=ProviderDB"
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
