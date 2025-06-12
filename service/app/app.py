from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from search import searchQuery
from bson import json_util
from json import loads
from os import getenv
from logging import getLogger

# Assuming the frontend is running on localhost:1234 or similar
# Override with CORS_ORIGINS environment variable
origins = loads(getenv('CORS_ORIGINS', '["http://localhost", "http://localhost:1234", "http://127.0.0.1", "http://127.0.0.1:1234"]'))

log = getLogger('uvicorn')

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    return {"message": f"Hello world!"}

@app.get("/search")
async def search(q: str = "", details: str = "n", lat: float | None = None, lon: float | None = None):
    res = await searchQuery(q, details, lat, lon, 5)
    return json_util.dumps(res)