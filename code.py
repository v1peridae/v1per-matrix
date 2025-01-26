import board
import displayio
import framebufferio
import rgbmatrix
import terminalio
from adafruit_bitmap_font import bitmap_font 
from adafruit_display_text import label 
from datetime import datetime, timedelta
import time
import requests
from io import BytesIO
import os
import dotenv

dotenv.load_dotenv()
API_KEY = os.getenv("API_KEY")


displayio.release_displays()
font = bitmap_font.load_font("antidote.bdf")

matrix = rgbmatrix.RGBMatrix(
    width=64, height=32, bit_depth=4,
    rgb_pins=[board.D6, board.D5, board.D9, board.D11, board.D10, board.D12],
    addr_pins=[board.A5, board.A4, board.A3, board.A2],
    clock_pin=board.D13, latch_pin=board.D0, output_enable_pin=board.D1
)

display = framebufferio.FramebufferDisplay(matrix, auto_refresh=False)

divider = displayio.Bitmap(1, 24, 1)
divider.fill(0)
divider_palette = displayio.Palette(1)
divider_palette[0] = 0xFFB6C1
divider = displayio.TileGrid(
    divider, pixel_shader=divider_palette, x=40, y=4)

date_line = label.Label(
    font,
    text="",
    color=0xFFFFFF
)
date_line.x = 3
date_line.y = 5

time_line = label.Label(
    font,
    text="",
    color=0xFFFFFF
)
time_line.x = 8
time_line.y = 14

weather_line = label.Label(
    font,
    text="",
    color=0xFFFFFF
)
weather_line.x = 2
weather_line.y = 22

temp_line = label.Label(
    font,
    text="",
    color=0xFFFFFF
)
temp_line.x = 45
temp_line.y = 5

bitmap = displayio.OnDiskBitmap("pngimg.com - hello_kitty_PNG22 (1).bmp")
img = displayio.TileGrid(bitmap, pixel_shader=bitmap.pixel_shader)
img.x = 43
img.y = 13

g = displayio.Group()
g.append(img)
g.append(divider)
g.append(date_line)
g.append(time_line)
g.append(temp_line)
g.append(weather_line)
display.root_group = g


def fetch_weather():
    url = "http://api.weatherapi.com/v1/forecast.json?key={API_KEY}&q=Nairobi&days=1&aqi=no&alerts=no"
    try:
        response = requests.get(url)
        if response.status_code == 200:
            return response.json()
    except:
        pass
    return None


last_update = 0
scroll_text = ""
scroll_pos = 0
last_scroll = 0

while True:
    now = datetime.now()
    home_time = now + timedelta(hours=3)
    current_time = home_time.strftime("%H:%M")
    current_date = home_time.strftime("%b %d")

    date_line.text = current_date
    time_line.text = current_time

    if time.time() - last_update > 300:
        weather_data = fetch_weather()
        if weather_data:
            temp_c = round(weather_data["current"]["temp_c"])
            temp_line.text = f"{temp_c}C"
            scroll_text = weather_data["current"]["condition"]["text"]
            scroll_pos = 0
        last_update = time.time()

    if time.time() - last_scroll > 0.3:
        if len(scroll_text) > 7:
            weather_line.text = (scroll_text + "    " +
                                 scroll_text)[scroll_pos:scroll_pos + 7]
            scroll_pos = (scroll_pos + 1) % (len(scroll_text) + 4)
        else:
            weather_line.text = scroll_text[:7]
        last_scroll = time.time()

    display.refresh(minimum_frames_per_second=0)
    time.sleep(0.1)
