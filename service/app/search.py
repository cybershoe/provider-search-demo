from pymongo import AsyncMongoClient
from pymongo.errors import ServerSelectionTimeoutError
from os import getenv
from logging import getLogger
import re
from json import dumps
from time import perf_counter

log = getLogger('uvicorn')

uri = getenv("MONGODB_URI", "mongodb://localhost:27017/")

client = AsyncMongoClient(uri)

db = client[getenv('MONGODB_DBNAME', 'providerDB')]
coll = db[getenv('MONGODB_COLLECTION', 'providers')]

rePostalCode = re.compile(r"[a-zA-Z]\d[a-zA-Z] ?[a-zA-Z]\d[a-zA-Z]")

async def searchQuery(query: str, details: str, lat: float | None, lon: float | None, count: int = 5) -> dict:
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
                'fuzzy': {},
                'score': {
                  'boost': {
                    'value': 2
                  }
                }
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
