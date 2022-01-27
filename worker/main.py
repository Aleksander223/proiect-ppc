from fastapi import FastAPI, status
from pymongo import MongoClient
from pydantic import BaseModel
from typing import List

app = FastAPI()

DB = "weather_db"
OBS_COLLECTION = "weather"


# Message class defined in Pydantic
class Observation(BaseModel):
    mo: int
    da: int
    temp: float
    stp: float
    wdsp: float
    mxspd: float
    gust: float
    max: float
    min: float
    prcp: float
    fog: int
    rain_drizzle: int
    snow_ice_pellets: int
    hail: int
    thunder: int
    name: str
    lat: float
    lon: float
    year: int


@app.post("/api/observation", status_code=status.HTTP_200_OK)
async def add_observation(observation: Observation):
    with MongoClient() as client:
        obs_collection = client[DB][OBS_COLLECTION]
        obs_collection.insert_one(observation.dict())
        return {"insertion": observation}


@app.get("/api/observation", response_model=List[Observation])
async def get_all_observations():
    with MongoClient() as client:
        obs_collection = client[DB][OBS_COLLECTION]
        all_observations = list(obs_collection.find({}))
        return all_observations


@app.get("/api/predict/")
async def predict(latitude: float, longitude: float, error: int = 5, days: int = 1):
    # apply the prediction alg ..

    return {
        "latitude": latitude,
        "longitude": longitude,
        "error": error,
        "days": days
    }
