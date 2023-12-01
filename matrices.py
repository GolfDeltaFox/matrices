from flask import Flask, send_file
from astro_weather_service import AstroWeatherService as Aws
import os
import random
import flask
import urllib
from flask_caching import Cache

app = Flask(__name__)
cache = Cache(app, config={"CACHE_TYPE": "simple"})

aws = Aws()

def cache_key():
    print(flask.request.url)
    return flask.request.url

@app.route('/matrices/astro/<longitude>/<latitude>/<zoom>')
@cache.cached(timeout=1800, key_prefix=cache_key)
def myapp(longitude, latitude, zoom):
    """
    Returns a random image directly through send_file
    """
    # longitude = 37.87
    # latitude = -122.27
    image = aws.call(longitude, latitude, int(zoom))
    return send_file(image, mimetype='image/png')