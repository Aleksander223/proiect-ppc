from pymongo import MongoClient
from fastapi import FastAPI, status
from pydantic import BaseModel
from typing import List

app = FastAPI()

DB = "weather_db"
OBS_COLLECTION = "weather"


# Message class defined in Pydantic
class Observation(BaseModel):
    year: int
    mo: int
    da: int
    temp: float
    stp: float
    wdsp: float
    mxpsd: float
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


@app.post("/api/observation", status_code=status.HTTP_200_OK)
async def add_observation(observation: Observation):
    with MongoClient() as client:
        obs_collection = client[DB][OBS_COLLECTION]
        obs_collection.insert_one(observation.dict())
        return {"insertion": observation}


@app.get("/api/observation", response_model=List[Observation])
async def get_all_observations(limit: int = 100):
    with MongoClient() as client:
        obs_collection = client[DB][OBS_COLLECTION]
        all_observations = list(obs_collection.find({}).limit(limit))
        return all_observations


@app.get("/api/observation/nearest", status_code=status.HTTP_200_OK, response_model=List[Observation])
async def get_nearest(latitude: float, longitude: float, error: int = 10, limit: int = 100):
    if (not (-180 <= longitude <= 180)) or (not (-90 <= latitude <= 90)):
        return {
            "error": "Check latitude and longitude"
        }

    with MongoClient() as client:
        obs_collection = client[DB][OBS_COLLECTION]
        all_observations = list(obs_collection.find({
            "location": {
                "$nearSphere": {
                    "$geometry": {
                        "type": "Point",
                        "coordinates": [longitude, latitude]
                    },
                    "$maxDistance": 1000 * error
                }
            }
        }).limit(limit))
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
