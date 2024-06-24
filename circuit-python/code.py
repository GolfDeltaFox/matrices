# Minimal example displaying an image tiled across multiple RGB LED matrices.
# This is written for MatrixPortal and four 64x32 pixel matrices, but could
# be adapted to different boards and matrix combinations.
# No additional libraries required, just uses displayio.
# Image wales.bmp should be in CIRCUITPY root directory.

import board
import displayio
import framebufferio
import rgbmatrix
import wifi
import io
import ssl
import socketpool
import adafruit_requests
import adafruit_imageload
from adafruit_display_text.label import Label 
import terminalio
from digitalio import DigitalInOut, Direction
import time


def get_display():
    displayio.release_displays() # Release current display, we'll create our own
    matrix = rgbmatrix.RGBMatrix(
        width=64, height=32, bit_depth=6,
        rgb_pins=[board.GP0, board.GP1, board.GP2, board.GP3, board.GP4, board.GP5],
        addr_pins=[board.GP6, board.GP7, board.GP8, board.GP9],
        clock_pin=board.GP11, latch_pin=board.GP12, output_enable_pin=board.GP13,
        tile=1, serpentine=True, doublebuffer=False)
    display = framebufferio.FramebufferDisplay(matrix, auto_refresh=False, rotation=180)
    return display

def display_print(display, text):
    display = get_display()
    group = displayio.Group()
    feed1_label = Label(terminalio.FONT, text=text, color=0xE39300, scale=1)
    feed1_label.x = 0
    feed1_label.y = 10
    group.append(feed1_label)
    display.show(group)
    time.sleep(1)
    display.refresh()


def display_image():
    print('updating')
    display = get_display()
    print('updating2')
    requests = adafruit_requests.Session(pool, ssl.create_default_context())
    response = requests.get("http://hera.local:5002/matrices/astro/37.87/-122.29/1")
    img_data = io.BytesIO(response.content)
    img, pal = adafruit_imageload.load(img_data)

    tile_grid = displayio.TileGrid(img, pixel_shader=pal)
    group = displayio.Group()
    group.append(tile_grid)
    display.show(group)
    display.refresh()


secrets = {'ssid':'Hestia','password':'M3rryChr157m45!'}
display = get_display()
display_print(display, "Hello!")
display_print(display, "Connecting\nto wifi.")

connected = False

while not connected:
    try:
        wifi.radio.connect(secrets['ssid'], secrets['password'])
        pool = socketpool.SocketPool(wifi.radio)
        display_print(display, "Connected!")
        connected = True
    except ConnectionError as e:
        display_print("Connection\nError,retrying")
        print("Connection Error:", e)
        print("Retrying in 10 seconds")
        time.sleep(10)


while True:
    display_image()
    time.sleep(600)


