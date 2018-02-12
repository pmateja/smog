#!/usr/bin/env python


import os
import plotly.graph_objs as go
from plotly.plotly import plot
from plotly.tools import set_credentials_file
from influxdb import InfluxDBClient
from datetime import datetime
from config import conf


layout = dict(
    title='<b>Stężenie pyłu zawieszonego w Gliwicach</b> \
    <br />ulica Derkacza',
    xaxis=dict(
        rangeselector=dict(
            buttons=list([
                dict(count=1, label='1d', step='day', stepmode='backward'),
                dict(count=2, label='2d', step='day', stepmode='backward'),
                dict(count=3, label='3d', step='day', stepmode='backward'),
                dict(count=7, label='7d', step='day', stepmode='backward'),
                dict(count=30, label='30d', step='day', stepmode='backward')
            ])
        ),
        rangeslider=dict(),
        type='date'
    )
)


def convtime(t):
    return datetime.strptime(t.split(".")[0], '%Y-%m-%dT%H:%M:%S')


def get_data_from_db():
    client = InfluxDBClient(**conf["influxdb"])
    result = client.query("select * from smog where time > now() - 30d;")
    result = result.items()[0][1]
    d = tuple((convtime(i["time"]), i["pm2.5"], i["pm10"]) for i in result)
    time = tuple(i[0] for i in d)
    pm25 = tuple(i[1] for i in d)
    pm10 = tuple(i[2] for i in d)
    return time, pm25, pm10


def make_plot():
    time, pm25, pm10 = get_data_from_db()
    plotly_username = conf["plotly"]["username"]
    plotly_key = conf["plotly"]["api_key"]
    plotly_filename = conf["plotly"]["filename"]
    plot_pm25 = go.Scatter(x=time, y=pm25, name="pm2.5")
    plot_pm10 = go.Scatter(x=time, y=pm10, name="pm10")
    set_credentials_file(
        username=plotly_username, api_key=plotly_key)
    out = plot(
        {"data": [plot_pm25, plot_pm10], "layout": layout},
        filename=plotly_filename,
        fileopt="overwrite",
        auto_open=False,
        sharing="public",
    )
    return out

if __name__ == "__main__":
    print("Plot created at: {}".format(make_plot()))
