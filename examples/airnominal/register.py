import random
import secrets
import string
import uuid
from typing import List

from fastapi import Depends, APIRouter
from pydantic import BaseModel

from auth import get_current_user
from mongo import stations, tokens

router = APIRouter()


class RegisterSensor(BaseModel):
    sensor_name: str
    quantity: str
    unit: str


class RegisterStation(BaseModel):
    station_name: str
    sensors: List[RegisterSensor]


class RegenrateToken(BaseModel):
    station_id: str


def generate_strings():
    used_strings = set()
    while True:
        new_string = ''.join(random.choices(string.ascii_uppercase + string.digits, k=3))
        if new_string not in used_strings and not new_string in ["END", "LAT", "LON"]:
            used_strings.add(new_string)
            yield new_string


def generate_password():
    alphabet = string.ascii_lowercase + string.digits
    password = ''.join(secrets.choice(alphabet) for i in range(6))
    return password


@router.post("/register")
async def register(register: RegisterStation, user=Depends(get_current_user)):
    gen = generate_strings()
    reg = dict(register)
    tok = {}
    reg["station_id"] = tok["station_id"] = str(uuid.uuid4())
    tok["token"] = generate_password()
    reg["lon"] = None
    reg["lat"] = None
    reg["updated"] = None
    for i, element in enumerate(reg["sensors"]):
        reg["sensors"][i] = dict(element)
        reg["sensors"][i]["sensor_id"] = str(uuid.uuid4())
        reg["sensors"][i]["short_id"] = next(gen)
    reg["owner_id"] = user["id"]
    reg["owner_name"] = user["display_name"]

    stations.insert_one(reg)
    tokens.insert_one(tok)
    rtn = reg.copy()
    rtn["token"] = tok["token"]
    rtn["_id"] = str(rtn["_id"])
    return rtn


@router.get("/my_stations")
async def get_my_stations(user=Depends(get_current_user)):
    print(stations.find({"owner_id": user["id"]}))
    return [station for station in stations.find({"owner_id": user["id"]}, {'_id': 0})]


class DeleteStation(BaseModel):
    id: str


@router.post("/delete_station")
async def delete_station(item: DeleteStation, user=Depends(get_current_user)):
    station = stations.delete_one({"station_id": item.id, "owner_id": user["id"]})
    return True
