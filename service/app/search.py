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

# Regex to match Canadian postal codes with or without space
rePostalCode = re.compile(r"[a-zA-Z]\d[a-zA-Z] ?\d[a-zA-Z]\d")

async def searchQuery(query: str, details: str, lat: float | None, lon: float | None, count: int = 5) -> dict:

  # Extract postal code from query if it exists and normalize
  match = re.search(rePostalCode, query)
  if match:
    postalCode = match.group()
    postalCode = postalCode.upper()
    if len(postalCode) == 6:
      postalCode = f"{postalCode[:3]} {postalCode[3:]}"
  else:
    postalCode = None

  # Aggregation pipeline for MongoDB Atlas Search
  agg = [{  
    '$search': {
      'index': 'providerSearch',
      
      # As a free-form search, entered terms could match a number of fields.
      # The `compound` operator allows us to combine multiple search 
      # conditions and use the sum of their scores to rank results.
      'compound': {
        'should': [{

              # The "autocomplete" operator breaks the query into substrings
              # and matches them against the substrings in the indexed fields.
              # This allows for partial matches and is useful for providing
              # suggestions as the user types.
              'autocomplete': {
                'query': query,
                'path': 'location.streetAddress',
                
                # Fuzzy matching allows for typos and variations, at the
                # cost of some additional processing time.
                'fuzzy': {}  
              }
            }, {
              'autocomplete': {
                'query': query,
                'path': 'location.municipality',
                'fuzzy': {}
              }
            }, {
              
              # The "text" operator performs a full-text search on the
              # specified field. It is useful for matching complete words
              # and phrases, and can be used in combination with other
              # operators to refine search results. In this case, because
              # the "province" field is too small to break into n-grams and
              # has low cardinality, we use the "text" operator instead
              # to match full tokens.
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
                
                # Search items can be weighted to influence the ranking of
                # results. In this case, matches on the last name are
                # given a higher score than matches on other fields, because
                # they are more likely to be the first thing a user would
                # think to type when searching for a provider.
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
 
  # If latitude and longitude are provided, we add a "near" operator to the
  # compount list of operators to give a higher score to results that are
  # closer to the specified location.    
  if (lat != None and lon != None):
    agg[0]["$search"]['compound']['should'].append({
      "near": {
        "path": "location.geoLocation",
        "origin": {
          "type": "Point",
          "coordinates": [lon, lat],
        },
        
        # The "pivot" parameter controls how distance from the origin affects
        # the score. A distance of "pivot" meters will give a score of 0.5,
        # with closer results scoring higher and farther results scoring lower.
        "pivot": 10000,
      }
    })

  # Some sorts of data will be an exact match, such as postal codes. Because
  # these are exact matches, we can use the "equals" operator against an
  # field that has been indexed with the "token" type for efficient matching.
  if postalCode:
    agg[0]["$search"]['compound']['should'].append({
      "equals": {
        "path": "location.postalCode",
        "value": postalCode,
        "score": {
          
          # Because postal codes are exact matches, we can give them a
          # higher score than other matches. This will ensure that results
          # with a matching postal code will appear at the top of the results.
          "constant": {
            "value": 10
          }
        }

      }
    })

  # Check the logs to see the final aggregation pipeline
  log.info(dumps(agg))


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
