#!/usr/bin/env python


from plotly.plotly import plot
import plotly.graph_objs as go
from plotly.tools import set_credentials_file
from influxdb import InfluxDBClient
from datetime import datetime
import os
import yaml


def get_config_file():
    """Ala ma kota"""
    local_config = os.path.join(
        os.path.dirname(os.path.realpath(__file__)),
        "config.yaml")
    home_config = os.path.join(
        os.path.expanduser("~"),
        ".smog", "config.yaml")
    if os.path.isfile(home_config):
        return home_config
    elif os.path.isfile(local_config):
        return local_config
    else:
        raise IOError("Config file not found")


def get_influx_config():
    with open(get_config_file()) as f:
        conf = yaml.load(f)
        influx = conf["influxdb"]
        return influx["host"], influx["port"], influx["user"], \
            influx["password"], influx["dbname"]


def get_plotly_config():
    with open(get_config_file()) as f:
        conf = yaml.load(f)
        plotly = conf["plotly"]
        return plotly["username"], plotly["api_key"], plotly["stream_ids"], \
            plotly["filename"]


def convtime(t):
    return datetime.strptime(t.split(".")[0], '%Y-%m-%dT%H:%M:%S')


if __name__ == "__main__":
    plotly_username, plotly_key, _, plotly_filename = get_plotly_config()
    influx_conf = get_influx_config()
    client = InfluxDBClient(*influx_conf)
    result = client.query("select * from smog where time > now() - 30d;")
    result = result.items()[0][1]
    d = tuple((convtime(i["time"]), i["pm2.5"], i["pm10"]) for i in result)
    time = tuple(i[0] for i in d)
    pm25 = tuple(i[1] for i in d)
    pm10 = tuple(i[2] for i in d)
    set_credentials_file(
        username=plotly_username, api_key=plotly_key)
    plot_pm25 = go.Scatter(x=time, y=pm25, name="pm2.5")
    plot_pm10 = go.Scatter(x=time, y=pm10, name="pm10")
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
    out = plot(
        {"data": [plot_pm25, plot_pm10], "layout": layout},
        filename=plotly_filename,
        fileopt="overwrite",
        auto_open=False,
        sharing="public",
    )
    print("Plot created at: {}".format(out))
