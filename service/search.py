from argparse import ArgumentParser
from faker import Faker
from sys import stdout
from random import choices, choice, randint
from pymongo import MongoClient
from bson import ObjectId
from json import load, dumps
from pprint import pprint


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

parser = ArgumentParser(
    prog="search.py",
    description="returns top n matches for a given autocorrect string"
)

parser.add_argument("-c", "--count", default=5)
parser.add_argument("query")

args = parser.parse_args()
count = int(args.count)
query = args.query

myAgg = [{  
    '$search': {
      'index': 'providerSearch',
      'compound': {
        'should': [{
              'autocomplete': {
                'query': "ajax kelly accupuncture",
                'path': 'location.streetAddress',
                'fuzzy': {}
              }
            }, {
              'autocomplete': {
                'query': "ajax kelly accupuncture",
                'path': 'location.municipality'
              }
            }, {
              'autocomplete': {
                'query': "ajax kelly accupuncture",
                'path': 'location.province'
                }
            }, {
              'autocomplete': {
                'query': "ajax kelly accupuncture",
                'path': 'location.postalCode'
                }
            }, {
              'autocomplete': {
                'query': "ajax kelly accupuncture",
                'path': 'name.first'
                }
            }, {
              'autocomplete': {
                'query': "ajax kelly accupuncture",
                'path': 'name.last'
                }
            }, {
              'autocomplete': {
                'query': "ajax kelly accupuncture",
                'path': 'telephone.main',
                'fuzzy': {}
                }
            }, {
              'autocomplete': {
                'query': "ajax kelly accupuncture",
                'path': 'telephone.fax',
                'fuzzy': {}
                }
            }, {
              'autocomplete': {
                'query': "ajax kelly accupuncture",
                'path': 'providerType'
                }
            }
        ]
      }
    }
  },
  {
    "$limit": 10
  },
  { "$addFields": {"score": {"$meta": "searchScore"}}}
  ]


def aggregation(query: str) -> dict:
  agg = [
    {
      '$search': {
        'index': 'providerSearch',
        'compound': {
            'should': [
              {
                'autocomplete': {
                  'query': query,
                  'path': 'location.streetAddress',
                  'fuzzy': {}
                }
              }, {
                'autocomplete': {
                  'query': query,
                  'path': 'location.municipality'
                }
              }, {
                'autocomplete': {
                  'query': query,
                  'path': 'location.province'
                  }
              }, {
                'autocomplete': {
                  'query': query,
                  'path': 'location.postalCode'
                  }
              }, {
                'autocomplete': {
                  'query': query,
                  'path': 'name.first'
                  }
              }, {
                'autocomplete': {
                  'query': query,
                  'path': 'name.last'
                  }
              }, {
                'autocomplete': {
                  'query': query,
                  'path': 'telephone.main',
                  'fuzzy': {}
                  }
              }, {
                'autocomplete': {
                  'query': query,
                  'path': 'telephone.fax',
                  'fuzzy': {}
                  }
              }, {
                'autocomplete': {
                  'query': query,
                  'path': 'providerType'
                  }
              }
          ]
        }
      }
    },
    {
      "$limit": count
    },
    { "$addFields": {"score": {"$meta": "searchScore"}}}
  ]

  agg[0]["$search"]['compound']['should'].append({
    "near": {
      "path": "location.geoLocation",
      "origin": {
        "type": "Point",
        "coordinates": [43.19797446394656, -79.59671581851744],
      },
      "pivot": 25000,
      "score": {
        "boost": { "value": 100 }
      }
    }
  })


  return agg


print(aggregation(query))

res = collection.aggregate(aggregation(query))
# res = collection.aggregate(aggregation(query))
for r in res:
  r['_id'] = str(r['_id'])
  print(dumps(r, indent=2))
print(count)