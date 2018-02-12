#!/usr/bin/env python3

import serial
from statistics import median
from datetime import datetime
from influxdb import InfluxDBClient
from time import sleep
from smog.config import conf


sensor = conf["sensor"]


def get_measures(quantity=5, delay=3*60):
    s = serial.Serial(sensor["port"], 9600)
    results = []
    for i in range(quantity):
        results.append(s.read(10))
        sleep(delay)
    pm25 = median([(i[3] * 256 + i[2])/10. for i in results])
    pm10 = median([(i[5] * 256 + i[4])/10. for i in results])
    return pm25, pm10


def send_data(pm25, pm10):
    json_body = [{
        "measurement": "smog",
        "tags": {
            "host": sensor["host"],
            "sensor": sensor["name"],
            "location": sensor["location"],
        },
        "fields": {
            "pm2.5": pm25,
            "pm10": pm10
        }
    }
    ]
    try:
        client = InfluxDBClient(**conf["influxdb"])
        client.write_points(json_body)
        print("Readings sent to the database")
    except:
        print("Error while sending data to the database")


if __name__ == "__main__":
    pm25, pm10 = get_measures()
    print("PM2.5: {}, PM10: {}".format(pm25, pm10))
    send_data(pm25, pm10)
