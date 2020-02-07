#!/usr/bin/python3
import requests
import re
from time import sleep
import cronus.beat as beat
from gpiozero import JamHat
import psutil

JAMHAT = JamHat()


def get_web_password():
    with open("/etc/pihole/setupVars.conf") as f:
        search = re.search(r"WEBPASSWORD=(?P<web_password>[a-z0-9]+)", f.read())
        return search.group("web_password")


def is_pihole_running():
    with open("/var/run/pihole-FTL.pid") as f:
        if psutil.pid_exists(f.read()):
            return True
        return False


def get_status():
    res = requests.get("http://localhost/admin/api.php")
    data = res.json()
    return data["status"] == "enabled"


def check_pihole_service():
    if not is_pihole_running():
        JAMHAT.lights_1.green.off()
        JAMHAT.lights_1.yellow.off()
        JAMHAT.lights_1.red.blink()
        return
    pihole_enabled = get_status()
    if pihole_enabled:
        JAMHAT.lights_1.green.on()
        JAMHAT.lights_1.yellow.off()
        JAMHAT.lights_1.red.off()
    else:
        JAMHAT.lights_1.green.off()
        JAMHAT.lights_1.red.off()
        JAMHAT.lights_1.yellow.blink()

def button_pressed():
    print('button pressed')

if __name__ == "__main__":
    JAMHAT.off()
    JAMHAT.button_1.when_pressed = button_pressed
    JAMHAT.lights_1.red.blink()
    JAMHAT.lights_2.red.blink()
    beat.set_rate(5 / 60)
    while beat.true():
        # Check pihole status
        check_pihole_service()

        beat.sleep()
