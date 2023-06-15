import datetime

from fastapi import APIRouter

from mongo import stations, tokens

router = APIRouter()
from pydantic import BaseModel
from influx import writeJsonToInflux

"""
f4174be6-5b5d-4094-8d38-644563608507_505524_0000000063FE3F23_DDF_3.1567_4DD_66567_LAT25.4_LON13.4END
UUUUUUUU-UUUU-UUUU-UUUU-UUUUUUUUUUUU_PPPPPP_TTTTTTTTTTTTTTTT_LAT_NNNN_LON_NNNN_XXX_NNNNNN_XXX_NNNNNEND

U - station uuid
P - password
X - 3 leter sensor code
N - sensor value
f - end of number
LAT - latitude
LON - longitude
END - stop of message, possible start of new message
T - unix time stamp in base 16

"""


def dataParser(raw: str):
    parsed = []
    print(raw)
    for dt in [x for x in raw.split("END") if len(x) > 0]:
        data = dt.split("_")
        print(data)
        uu = data[0]
        pas = data[1]
        if "T" in data[2]:
            time = datetime.datetime.utcnow().isoformat()
        else:
            time = datetime.datetime.utcfromtimestamp(int(data[2], base=16)).isoformat()
        lat = float(data[4])
        lon = float(data[6])
        sensor_data = []
        for i in range(7, len(data), 2):
            sen = data[i]
            dat = float(data[i + 1])
            sensor_data.append({
                "short_id": sen,
                "data": dat
            })
        parsed.append({
            "station_id": uu,
            "token": pas,
            "time": time,
            "lat": lat,
            "lon": lon,
            "data": sensor_data
        })
    print(parsed)
    return parsed


"""
p = influxdb_client.Point("data").from_dict(
        
            {
                "measurement": "data",
                "tags": {
                    "owner_id": "1235989238",
                    "owner_name": "Alenka Mozer",
                    "station_id": "3894838983",
                    "station_name": "test station",
                    "sensor_id": "878754375",
                    "sensor_name": "CO2-01",
                    "display_quantity": "CO2 (ppm)",
                    "quantity": "CO2",
                    "unit": "ppm"
                },
                "time": random_date_time(),
                "fields": {
                    "lat": random.uniform(-180, 180),
                    "lon": random.uniform(-90, 90),
                    "value": random.uniform(0, 30)
                }
            }
        
    )
"""


def influxDataTransformer(parsed_object):
    query = {"station_id": parsed_object["station_id"]}
    station = stations.find_one(query)
    token = tokens.find_one(query)
    if parsed_object["token"] != token["token"]:
        return False
    for point in parsed_object["data"]:
        sensor = [sen for sen in station["sensors"] if sen["short_id"] == point["short_id"]][0]
        writeJsonToInflux({
            "measurement": "data",
            "tags": {
                "owner_id": station["owner_id"],
                "owner_name": station["owner_name"],
                "station_id": parsed_object["station_id"],
                "station_name": station["station_name"],
                "sensor_id": sensor["sensor_id"],
                "sensor_name": sensor["sensor_name"],
                "display_quantity": sensor["quantity"] + " (" + sensor["unit"] + ")",
                "quantity": sensor["quantity"],
                "unit": sensor["unit"]
            },
            "time": parsed_object["time"],
            "fields": {
                "lat": parsed_object["lat"],
                "lon": parsed_object["lon"],
                "value": point["data"]
            }
        })
    time = datetime.datetime.fromisoformat(parsed_object["time"] + "+00:00")
    update = {"$set": {"lat": parsed_object["lat"], "lon": parsed_object["lon"], "updated": time}}
    stations.update_one(query, update)


class DataPost(BaseModel):
    data: str


@router.post("/data")
async def ingest_data(item: DataPost):
    for point in dataParser(item.data):
        influxDataTransformer(point)
    return True


@router.post("/data_url")
async def ingest_data(item: str = ""):
    if item != "":
        for point in dataParser(item):
            influxDataTransformer(point)
    return True
