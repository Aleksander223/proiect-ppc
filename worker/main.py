from pymongo import MongoClient
from fastapi import FastAPI, status
from pydantic import BaseModel
from typing import List
from arima import predict
import pandas as pd

app = FastAPI()

DB = "weather_db"
OBS_COLLECTION = "weather"
DB_URL = "mongodb://mongo:27017/"


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
    with MongoClient(DB_URL) as client:
        obs_collection = client[DB][OBS_COLLECTION]
        obs_collection.insert_one(observation.dict())
        return {"insertion": observation}


@app.get("/api/observation", response_model=List[Observation])
async def get_all_observations(limit: int = 100):
    with MongoClient(DB_URL) as client:
        obs_collection = client[DB][OBS_COLLECTION]
        all_observations = list(obs_collection.find({}).limit(limit))
        return all_observations


@app.get("/api/observation/nearest", status_code=status.HTTP_200_OK, response_model=List[Observation])
async def get_nearest(latitude: float, longitude: float, error: int = 10, limit: int = 100):
    if (not (-180 <= longitude <= 180)) or (not (-90 <= latitude <= 90)):
        return {
            "error": "Check latitude and longitude"
        }

    with MongoClient(DB_URL) as client:
        obs_collection = client[DB][OBS_COLLECTION]
        closest_station = list(obs_collection.find({
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

        if not closest_station:
            return {
            "error": "Increase error; no station found"
        }

        station_name = closest_station[0]["name"]

        station_observations = list(obs_collection.find({
            "name": station_name
        }))

        return station_observations


@app.get("/api/predict")
async def forecast(latitude: float, longitude: float, error: int = 5, days: int = 1):
    if (not (-180 <= longitude <= 180)) or (not (-90 <= latitude <= 90)):
        return {
            "error": "Check latitude and longitude"
        }

    # apply the prediction alg ..

    with MongoClient(DB_URL) as client:
        obs_collection = client[DB][OBS_COLLECTION]
        closest_station = list(obs_collection.find({
            "location": {
                "$nearSphere": {
                    "$geometry": {
                        "type": "Point",
                        "coordinates": [longitude, latitude]
                    },
                    "$maxDistance": 1000 * error
                }
            }
        }).limit(100))

        if not closest_station:
            return {
            "error": "Increase error; no station found"
        }

        station_name = closest_station[0]["name"]

        station_observations = list(obs_collection.find({
            "name": station_name
        }))

        data = pd.DataFrame(station_observations)

        predicted_temperature = predict(data, days, col='temp')
        predicted_max = predict(data, days, col='max')
        predicted_min = predict(data, days, col='min')
        predicted_fog = predict(data, days, col='fog')
        predicted_hail = predict(data, days, col='hail')
        predicted_rain = predict(data, days, col='rain_drizzle')
        predicted_snow_ice_pellets = predict(data, days, col='snow_ice_pellets')
        predicted_thunder = predict(data, days, col='thunder')

        df = pd.DataFrame()
        df["temp"] = predicted_temperature.array
        df["max_temp"] = predicted_max.array
        df["min_temp"] = predicted_min.array
        df["fog"] = predicted_fog.array
        df["hail"] = predicted_hail.array
        df["rain"] = predicted_rain.array
        df["snow"] = predicted_snow_ice_pellets.array
        df["thunder"] = predicted_thunder.array

        df["temp"] = df["temp"].transform(lambda x: (x-32)*5/9)
        df["max_temp"] = df["max_temp"].transform(lambda x: (x-32)*5/9)
        df["min_temp"] = df["min_temp"].transform(lambda x: (x-32)*5/9)

        # predictions = pd.concat([predicted_temperature, predicted_max, predicted_min, predicted_fog, predicted_hail, predicted_rain, predicted_snow_ice_pellets, predicted_thunder])

        return {
            "result": df.to_dict('records')
        }
