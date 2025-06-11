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
collection = db['addresses']


with open("area_codes.json") as ac:
  area_codes = load(ac)

def genNumber(city: str, tollFreeRatio: float = 0.25) -> str:

  if (not area_codes.get(city)) or choices([True, False],[tollFreeRatio, 1-tollFreeRatio])[0]:
    areaCode = choice(["800","877","866","855","844"])
  else:
    areaCode = choice(area_codes[city])
  return f"{areaCode}-{str(randint(2, 999)).zfill(3)}-{str(randint(0, 9999)).zfill(4)}"

provider_types = [
    ("Chiropractor", 80),
    ("Registered Massage Therapist", 0),
    ("Physiotherapist", 0),
    ("Acupuncturist", 15),
    ("Osteopath", 0)
]


parser = ArgumentParser(
    prog="Provider Generator",
    description="Generates a JSON file containing randomly-generated service providers for the autocomplete demo"
)

parser.add_argument("-c", "--count", required=True)
parser.add_argument("-o", "--outfile")

args = parser.parse_args()
count = int(args.count)
outfile = args.outfile

cityAgggregation  = [

  {
    "$sample":{
      "size": count
    }
  },
  {
    "$replaceRoot": { 
      "newRoot": "$Address" 
    }
  }
]


addresses = collection.aggregate(cityAgggregation)

fake = Faker(locale="en_CA")

firstline = True

with open(args.outfile, mode="w") if args.outfile else stdout as out:

  for i in range(count):
      out.write("[" if firstline else ",\n")
      firstline = False
      provider_type, dr_chance = choices(provider_types)[0]
      gender = choices(("m", "f", "x"), weights=[44,52,3])[0]
      match gender:
          case "m":
              firstname = fake.first_name_male()
              prefix = "Mr."
          case "f":
              firstname = fake.first_name_female()
              prefix = choices(["Mrs.", "Ms."], weights=[2,3])[0]
          case "x":
              firstname = fake.first_name_nonbinary()
              prefix = "Mx."
          case _:
              raise RuntimeError
          
      prefix = choices(("Dr.", prefix), cum_weights=[dr_chance, 100])[0]
      address = addresses.next()


          
      person = {
          "name":{ 
              "first": firstname,
              "last": fake.last_name(),
              "prefix": prefix
          },
          "location": {
              "streetAddress": f"{address['Number']} {address['Street'].title()}",
              "municipality": address['City'].title(),
              "province": address['Provience'].upper(),
              "postalCode": address['Postal Code'],
              "geoLocation": address['location']
          },
          "telephone": {
            "main":  genNumber(address['City'].title(), 0.2) ,
            "fax": genNumber(address['City'].title(), 0.05)
          },
          "providerType": provider_type
      }

      out.write(dumps(person, indent=2))
  out.write("]\n") 
