from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from faker import Faker
from search import searchQuery
from bson import ObjectId, json_util
from json import dumps
from logging import getLogger
from pprint import pformat

origins = [
    "http://localhost",
    "http://localhost:1234",
    "http://127.0.0.1",
    "http://127.0.0.1:1234",
]


log = getLogger()

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

fake = Faker(locale="en_CA")

@app.get("/")
async def root():
    return {"message": f"Hello {fake.name()} from {fake.address()}"}

@app.get("/search")
async def search(q: str = "", details: str = "n", lat: float | None = None, lon: float | None = None):
    res = await searchQuery(q, details, lat, lon, 5)

    # async for r in res:
    #     r['_id'] = str(r['_id'])
    #     foo.append(pformat(r))
    return json_util.dumps(res)