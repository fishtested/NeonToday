import adafruit_display_text.label
import board
import displayio
import framebufferio
import rgbmatrix
import terminalio
import time
from adafruit_bitmap_font import bitmap_font
from displayio import Bitmap
import logging
import requests
import threading

logging.basicConfig(level=logging.DEBUG, format='%(message)s')
start_time = time.monotonic()

font = bitmap_font.load_font("5x5FontMonospaced-5.bdf", Bitmap)

displayio.release_displays()

matrix = rgbmatrix.RGBMatrix(
    width=64, height=32, bit_depth=1,
    rgb_pins=[board.D6, board.D5, board.D9, board.D11, board.D10, board.D12],
    addr_pins=[board.A5, board.A4, board.A3, board.A2],
    clock_pin=board.D13, latch_pin=board.D0, output_enable_pin=board.D1)
display = framebufferio.FramebufferDisplay(matrix, auto_refresh=False)

# Date and Time
timeline = adafruit_display_text.label.Label(
    terminalio.FONT,
    color=0xC40054,
    text=""
)
timeline.x = 2
timeline.y = 7

dateline = adafruit_display_text.label.Label(
    terminalio.FONT,
    color=0x338994,
    text=""
)
dateline.x = 2
dateline.y = 23

dateandtime = displayio.Group()
dateandtime.append(timeline)
dateandtime.append(dateline)

# Weather
# Conditions
conditionsline = adafruit_display_text.label.Label(
    font,
    color=0xC40054,
    text="Loading"
)
conditionsline.x = 1
conditionsline.y = 4

# Temperature
temperatureline = adafruit_display_text.label.Label(
    font,
    color=0xE19C13,
    text="T: -- °C"
)
temperatureline.x = 2
temperatureline.y = 12

# Apparent
apparentline = adafruit_display_text.label.Label(
    font,
    color=0x23FBE0,
    text="A: -- °C"
)
apparentline.x = 2
apparentline.y = 20

# Low
lowline = adafruit_display_text.label.Label(
    font,
    color=0x23FBE0,
    text="--"
)
lowline.x = 1
lowline.y = 28

# High
highline = adafruit_display_text.label.Label(
    font,
    color=0xC40054,
    text="--"
)
highline.x = 35
highline.y = 28

weather_group = displayio.Group()
weather_group.append(conditionsline)
weather_group.append(temperatureline)
weather_group.append(apparentline)
weather_group.append(lowline)
weather_group.append(highline)

# Get Weather Data
def get_data():
    global temperature, apparent_temperature, codetext, high_temperature, low_temperature
    url = 'https://api.open-meteo.com/v1/forecast?latitude=12.34&longitude=56.78&current=temperature_2m,apparent_temperature&daily=weather_code,temperature_2m_max,temperature_2m_min&forecast_days=1'
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        temperature = data['current']['temperature_2m']
        apparent_temperature = data['current']['apparent_temperature']
        code = data['daily']['weather_code']
        high_temperature = data['daily']['temperature_2m_max'][0]
        low_temperature = data['daily']['temperature_2m_min'][0]

        # Change major weather codes to text
        if code == [0]:
            codetext = "Clear"
        elif code == [1]:
            codetext = "Most Clear"
        elif code == [2]:
            codetext = "Part Cloud"
        elif code == [3]:
            codetext = "Cloudy"
        elif code == [45]:
            codetext = "Fog"
        elif code == [48]:
            codetext = "Frz Fog"
        elif code == [51]:
            codetext = "Lt Drizzle"
        elif code == [53]:
            codetext = "Drizzle"
        elif code == [55]:
            codetext = "Hv Drizzle"
        elif code == [56]:
            codetext = "Lt Fz Drzl"
        elif code == [57]:
            codetext = "Fz Drizzle"
        elif code == [61]:
            codetext = "Light Rain"
        elif code == [63]:
            codetext = "Rain"
        elif code == [65]:
            codetext = "Heavy Rain"
        elif code == [66]:
            codetext = "Lt Fz Rain"
        elif code == [67]:
            codetext = "Frz Rain"
        elif code == [71]:
            codetext = "Light Snow"
        elif code == [73]:
            codetext = "Snow"
        elif code == [75]:
            codetext = "Heavy Snow"
        elif code == [77]:
            codetext = "Snow Grain"
        elif code == [80]:
            codetext = "Lt Rain Sh"
        elif code == [81]:
            codetext = "Rain Showr"
        elif code == [82]:
            codetext = "Hv Rain Sh"
        elif code == [85]:
            codetext = "Lt Snow Sh"
        elif code == [86]:
            codetext = "Snow Showr"

        conditionsline.text = str(codetext)
        temperatureline.text = "T: " + str(temperature) + " °C"
        apparentline.text = "A: " + str(apparent_temperature) + " °C"
        lowline.text = str(low_temperature)
        highline.text = str(high_temperature)

        display.refresh(minimum_frames_per_second=25)
        logging.info('Weather data updated and display refreshed!')

def get_data_schedule():
    get_data()
    threading.Timer(1800, get_data_schedule).start()

get_data_schedule()

group_displayed = 0
display.root_group = dateandtime

while True:
    current_time = time.localtime()
    formatted_time = "{:02}:{:02}:{:02}".format(current_time.tm_hour, current_time.tm_min, current_time.tm_sec)
    timeline.text = formatted_time
    formatted_date = time.strftime("%Y-%m-%d", current_time)
    dateline.text = formatted_date
    display.refresh(minimum_frames_per_second=25)

    elapsed_time = time.monotonic() - start_time
    logging.info(elapsed_time)
    if elapsed_time >= 15:
        if group_displayed == 0:
            display.root_group = weather_group
            logging.info('Changed to weather_group')
            group_displayed = 1
            logging.info('Changed to 1')
        else:
            display.root_group = dateandtime
            logging.info('Changed to dateandtime')
            group_displayed = 0
            logging.info('Changed to 0')
        start_time = time.monotonic()

    time.sleep(0.1)
