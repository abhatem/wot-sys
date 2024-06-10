import board
import adafruit_dotstar as dotstar
import requests
import socket
import time
import json
import _thread
from random import randint
from flask import Flask, request, abort
from td import get_td


# ---------------- CONFIG ----------------
TD_DIRECTORY_ADDRESS = "http://192.168.0.100:8080"
LISTENING_PORT = 8080
DEFAULT_BRIGHTNESS = 0.5
# Number of LEDs in each strip
UPPER = 39
MIDDLE = 40
LOWER = 39
NR_OF_LEDS = UPPER + MIDDLE + LOWER
# ----------------------------------------


app = Flask(__name__)
dots = dotstar.DotStar(board.SCK, board.MOSI, NR_OF_LEDS, brightness=DEFAULT_BRIGHTNESS)


@app.route("/")
def thing_description():
    return json.dumps(get_td(ip_addr, NR_OF_LEDS)), {'Content-Type': 'application/json'}


@app.route("/properties/brightness", methods=["GET", "PUT"])
def brightness():
    if request.method == "PUT":
        if request.is_json:
            if type(request.json) == int and 0 <= request.json <= 100:
                dots.brightness = request.json / 100
                return "", 204
            else:
                abort(400)
        else:
            abort(415)
    else:
        return str(int(dots.brightness * 100)), {'Content-Type': 'application/json'}


@app.route("/properties/stats", methods=["GET"])
def led_stats():
    res = {"nr_of_leds": NR_OF_LEDS, "nr_of_led_on": 0, "brightness": int(dots.brightness * 100), "leds": []}
    for i in range(NR_OF_LEDS):
        if dots[i] != (0, 0, 0):
            res["nr_of_led_on"] += 1
        res["leds"].append(dots[i])
    return json.dumps(res), {'Content-Type': 'application/json'}


@app.route("/actions/dot", methods=["POST"])
def dot():
    if request.is_json:
        try:
            led = request.json["led"]
            color = request.json["color"]
            dots[int(led)] = (int(color["red"]), int(color["green"]), int(color["blue"]))
            return "", 204
        except Exception as e:
            print(e)
            abort(400)
    else:
        abort(415)  # Wrong media type.

@app.route("/actions/fill_array", methods=["POST"])
def fill_array():
    if request.is_json:
        try:
            ledBegin = request.json["ledBegin"]
            ledEnd = request.json["ledEnd"]
            color = request.json["color"]
            for led in range(ledBegin, ledEnd):
                dots[int(led)] = (int(color["red"]), int(color["green"]), int(color["blue"]))
            return "", 204
        except Exception as e:
            print(e)
            abort(400)
    else:
        abort(415)  # Wrong media type.

@app.route("/actions/fill", methods=["POST"])
def fill():
    if request.is_json:
        for i in range(NR_OF_LEDS):
            dots[i] = (int(request.json["red"]), int(request.json["green"]), int(request.json["blue"]))
        return "", 204
    else:
        abort(415)  # Wrong media type.


@app.route("/actions/fill_upper", methods=["POST"])
def fill_upper():
    if request.is_json:
        for i in range(UPPER):
            dots[i] = (int(request.json["red"]), int(request.json["green"]), int(request.json["blue"]))
        return "", 204
    else:
        abort(415)  # Wrong media type.


@app.route("/actions/fill_middle", methods=["POST"])
def fill_middle():
    if request.is_json:
        for i in range(UPPER, UPPER+MIDDLE):
            dots[i] = (int(request.json["red"]), int(request.json["green"]), int(request.json["blue"]))
        return "", 204
    else:
        abort(415)  # Wrong media type.


@app.route("/actions/fill_lower", methods=["POST"])
def fill_lower():
    if request.is_json:
        for i in range(UPPER+MIDDLE, NR_OF_LEDS):
            dots[i] = (int(request.json["red"]), int(request.json["green"]), int(request.json["blue"]))
        return "", 204
    else:
        abort(415)  # Wrong media type.


@app.route("/actions/random", methods=["POST"])
def random():
    for i in range(NR_OF_LEDS):
        dots[i] = (randint(0, 255), randint(0, 255), randint(0, 255))
    return "", 204



@app.route("/actions/shutdown", methods=["POST"])
def shutdown():
    for i in range(NR_OF_LEDS):
        dots[i] = (0, 0, 0)
    return "", 204


def submit_td(ip_addr, nr_of_leds):
    td = get_td(ip_addr, nr_of_leds)
    print("Uploading TD to directory ...")
    while True:
        try:
            r = requests.post("{}/td".format(TD_DIRECTORY_ADDRESS), json=td)
            r.close()
            print("Got response: ", r.status_code)
            if 200 <= r.status_code <= 299:
                print("TD uploaded!")
                return
        except Exception as e:
            print(e)
            print("TD could not be uploaded. Will try again in 15 Seconds...")
            time.sleep(15)


# wait for Wifi to connect
s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
while True:
    try:
        s.connect(('192.168.0.1', 80))  # connect to router to ensure a successful connection
        ip_addr = s.getsockname()[0] + ":" + str(LISTENING_PORT)
        break
    except OSError:
        time.sleep(3)

# Submit TD to directory
_thread.start_new_thread(submit_td, (ip_addr, NR_OF_LEDS))

# Run app server
app.run(host='0.0.0.0', port=8080)
