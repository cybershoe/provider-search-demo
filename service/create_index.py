from argparse import ArgumentParser
from faker import Faker
from sys import stdout
from random import choices, choice, randint
from pymongo import MongoClient
from json import load, dumps




MONGO_URI = uri = "mongodb+srv://providerdb.bzepjj.mongodb.net/?authSource=%24external&authMechanism=MONGODB-X509&retryWrites=true&w=majority&appName=ProviderDB"
# Create a new client and connect to the server
client = MongoClient(
    uri,
    tls=True,
    tlsCertificateKeyFile="keys/X509-cert-4247274353405106559.pem",
    authMechanism="MONGODB-X509"
    )

db = client['Generator']
collection = db['providers']

mongoClient = MongoClient()

collection.create_search_index({"name": "providerSearch", "definition":
  {
  "mappings": {
    "dynamic": False,
    "fields": {
      "name.first": {
          "type": "autocomplete",
      },
      "name.last": {
          "type": "autocomplete",
      },
      "location.streetAddress" : {
          "type": "autocomplete"
      },
      "location.municipality" : {
          "type": "autocomplete"
      },
      "telephone.main": {
        	"type": "autocomplete",
        	"analyzer": "lucene.simple" 
      }
    } 
  }
}}
)