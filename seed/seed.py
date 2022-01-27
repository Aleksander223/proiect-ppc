import pandas as pd
import pymongo
from pymongo import MongoClient
from tqdm import tqdm

fileLocation = "C:/Users/Aleks/Documents/dosart/testtttt/5_year_weather_data.csv"
dbUrl = "mongodb://localhost:27017/"
dbName = "weather_db"
collName = "weather"

df = pd.read_csv(fileLocation)

client = MongoClient(dbUrl)

db = client[dbName]
coll = db[collName]

coll.create_index([("location", "2dsphere")])

for index, row in tqdm(df.iterrows(), total=df.shape[0]):
    observation = {}

    for col in df.columns:
        observation[col] = row[col]

    observation["location"] = {
        "type": "Point",
        "coordinates": [observation["lon"], observation["lat"]]
    }

    observation.pop("lat")
    observation.pop("lon")

    coll.insert_one(observation)
    