import influxdb_client
from influxdb_client.client.write_api import SYNCHRONOUS

from config import bucket, org, token
from config import influx_url as url

client = influxdb_client.InfluxDBClient(
    url=url,
    token=token,
    org=org
)

# Write script
write_api = client.write_api(write_options=SYNCHRONOUS)


def writeJsonToInflux(dict):
    print(dict)
    p = influxdb_client.Point("data").from_dict(dict)
    write_api.write(bucket=bucket, org=org, record=p)
