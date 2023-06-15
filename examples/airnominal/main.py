import influxdb_client
from fastapi import FastAPI
from influxdb_client.client.write_api import SYNCHRONOUS

from auth import router as auth_router
from config import api_root_path
from data_endpoint import router as data_router
from register import router as register_router

# config for influx-db
bucket = "Airnominal-data2"
org = "Airnominal"
token = "DFUh1vGGeC2UHrAY8UW-t_3ylXa5LLo7mID-vaZ8UFgaggNjqRpz_lxmNErbazdJQA7q_F8stomdWK_YVHaE1A=="
url = "http://192.168.64.10:8086"

client = influxdb_client.InfluxDBClient(
    url=url,
    token=token,
    org=org
)

write_api = client.write_api(write_options=SYNCHRONOUS)

app = FastAPI(root_path=api_root_path)
app.include_router(auth_router)
app.include_router(register_router)
app.include_router(data_router)
