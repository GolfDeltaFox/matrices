from flask import Flask, send_file
from astro_weather_service import AstroWeatherService as Aws
import os
import random
app = Flask(__name__)
aws = Aws()


@app.route('/matrices/astro/<longitude>/<latitude>/<zoom>')
def myapp(longitude, latitude, zoom):
    """
    Returns a random image directly through send_file
    """
    # longitude = 37.87
    # latitude = -122.27
    image = aws.call(longitude, latitude, int(zoom))
    return send_file(image, mimetype='image/png')