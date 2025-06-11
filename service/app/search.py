from pymongo import MongoClient, AsyncMongoClient
from pymongo.errors import ServerSelectionTimeoutError
from pprint import pformat
from logging import getLogger
import re
from json import dumps
from time import perf_counter

log = getLogger('uvicorn')

MONGO_URI = uri = "mongodb+srv://providerdb.bzepjj.mongodb.net/?authSource=%24external&authMechanism=MONGODB-X509&retryWrites=true&w=majority&appName=ProviderDB"

client = AsyncMongoClient(
    uri,
    tls=True,
    tlsCertificateKeyFile="keys/X509-cert-4247274353405106559.pem",
    authMechanism="MONGODB-X509",
    # timeoutMS= 10000
    )

db = client['Generator']
coll = db['providers']

rePostalCode = re.compile(r"[a-zA-Z]\d[a-zA-Z] ?[a-zA-Z]\d[a-zA-Z]")

async def searchQuery(query: str, details: str, lat: float | None, lon: float | None, count: int = 5) -> tuple[dict, float]:
  log.info(details)
  match = re.search(rePostalCode, query)
  if match:
    postalCode = match.group()
    postalCode = postalCode.upper()
    if len(postalCode) == 6:
      postalCode = f"{postalCode[:3]} {postalCode[3:]}"
  else:
    postalCode = None

  agg = [{  
    '$search': {
      'index': 'providerSearch',
      'compound': {
        'should': [{
              'autocomplete': {
                'query': query,
                'path': 'location.streetAddress',
                'fuzzy': {}
              }
            }, {
              'autocomplete': {
                'query': query,
                'path': 'location.municipality',
                'fuzzy': {}
              }
            }, {
              'text': {
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
                'path': 'name.first',
                'fuzzy': {}
                }
            }, {
              'autocomplete': {
                'query': query,
                'path': 'name.last',
                'fuzzy': {}
                }
            }, {
              'autocomplete': {
                'query': query,
                'path': 'telephone.main',
                }
            }, {
              'autocomplete': {
                'query': query,
                'path': 'telephone.fax',
                }
            }, {
              'autocomplete': {
                'query': query,
                'path': 'providerType',
                'fuzzy': {}
                }
            }
        ]
      },
      "scoreDetails": True if details == "y" else False
    }
  },
  {
    "$limit": count
  },
  { "$addFields": {"score": {"$meta": "searchScore"}, "scoreDetails": {"$meta": "searchScoreDetails"}}}
  ]

  log.info(dumps(agg))

  if (lat != None and lon != None):
    agg[0]["$search"]['compound']['should'].append({
      "near": {
        "path": "location.geoLocation",
        "origin": {
          "type": "Point",
          "coordinates": [lon, lat],
        },
        "pivot": 10000,
      }
    })

  if postalCode:
    agg[0]["$search"]['compound']['should'].append({
      "equals": {
        "path": "location.postalCode",
        "value": postalCode,
        "score": {
          "constant": {
            "value": 10
          }
        }

      }
    })

  try: 
    startTime = perf_counter()
    cursor = await coll.aggregate(agg)
    stopTime = perf_counter()
    log.info(f"Database time: {stopTime-startTime}s")
    docs = await cursor.to_list()
    results = {
      "results": docs,
      "databaseTime": stopTime - startTime
    }
    return results
  except ServerSelectionTimeoutError:
    return {
      "results": [],
      "databaseTime": -1,
      "error": "Timed out"
    }
  except Exception as e:
    return {
      "results": [],
      "databaseTime": -1,
      "error": repr(e)
    }
