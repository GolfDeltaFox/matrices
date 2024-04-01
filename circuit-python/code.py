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
from digitalio import DigitalInOut, Direction
import time

wifi.radio.connect("SSID", "Pwd")

pool = socketpool.SocketPool(wifi.radio)

bit_depth_value = 4
base_width = 64
base_height = 32
chain_across = 1
tile_down = 1
serpentine_value = True

width_value = base_width * chain_across
height_value = base_height * tile_down

def display():
    print('updating')
    requests = adafruit_requests.Session(pool, ssl.create_default_context())
    response = requests.get("http://hera.local:5002/matrices/astro/37.87/-122/1")
    img_data = io.BytesIO(response.content)
    #img, pal = adafruit_imageload.load('test.png', bitmap=displayio.Bitmap, palette=displayio.Palette)
    img, pal = adafruit_imageload.load(img_data)
    # img, pal = adafruit_imageload.load('test.bmp')




    displayio.release_displays() # Release current display, we'll create our own


    # matrix = rgbmatrix.RGBMatrix(
    #     width=width_value, height=height_value, bit_depth=bit_depth_value,
    #     rgb_pins=[board.GP2, board.GP3, board.GP4, board.GP5, board.GP8, board.GP9],
    #     addr_pins=[board.GP10, board.GP16, board.GP18, board.GP20],
    #     clock_pin=board.GP11, latch_pin=board.GP12, output_enable_pin=board.GP13,
    #     tile=tile_down, serpentine=serpentine_value,
    #     doublebuffer=False)

    #Pinout for Interstate 75W
    matrix = rgbmatrix.RGBMatrix(
        width=64, height=32, bit_depth=6,
        rgb_pins=[board.GP0, board.GP1, board.GP2, board.GP3, board.GP4, board.GP5],
        addr_pins=[board.GP6, board.GP7, board.GP8, board.GP9],
        clock_pin=board.GP11, latch_pin=board.GP12, output_enable_pin=board.GP13,
        tile=tile_down, serpentine=serpentine_value, doublebuffer=False)
    

    DISPLAY = framebufferio.FramebufferDisplay(matrix, auto_refresh=False,
                                               rotation=180)


    tile_grid = displayio.TileGrid(img, pixel_shader=pal)
    group = displayio.Group()
    group.append(tile_grid)
    DISPLAY.show(group)
    DISPLAY.refresh()

while True:
    display()
    time.sleep(600)

