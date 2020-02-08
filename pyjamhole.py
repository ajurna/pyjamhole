#!/usr/bin/python3
import re

import cronus.beat as beat
import psutil
import requests
from gpiozero import JamHat
from loguru import logger

JAMHAT = JamHat()
URL = "http://localhost/admin/api.php"
DISABLE_TIME = 300

def get_web_password():
    with open("/etc/pihole/setupVars.conf") as f:
        search = re.search(r"WEBPASSWORD=(?P<web_password>[a-z0-9]+)", f.read())
        return search.group("web_password")


def is_pihole_running():
    with open("/var/run/pihole-FTL.pid") as f:
        if psutil.pid_exists(int(f.read().strip())):
            return True
        return False


def get_status():
    res = requests.get(URL)
    data = res.json()
    return data["status"] == "enabled"


def check_pihole_service():
    if not is_pihole_running():
        JAMHAT.lights_1.green.off()
        JAMHAT.lights_1.yellow.off()
        JAMHAT.lights_1.red.blink()
        logger.info("pihole not running")
        return
    pihole_enabled = get_status()
    if pihole_enabled:
        JAMHAT.lights_1.off()
        JAMHAT.lights_1.green.on()
        logger.info("service running")
    else:
        JAMHAT.lights_1.green.off()
        JAMHAT.lights_1.red.off()
        JAMHAT.lights_1.yellow.blink()
        logger.info("service running not blocking")


def disable_button():
    logger.info("disable button pressed")
    r = requests.get(URL, params={"disable": DISABLE_TIME, "auth": get_web_password()})
    check_pihole_service()


def enable_button():
    logger.info("enable button pressed")
    r = requests.get(URL, params={"enable": True, "auth": get_web_password()})
    check_pihole_service()

def check_pihole_version():
    r = requests.get(URL, params={"versions": True})
    data = r.json()
    logger.debug(data)
    if data["core_update"] or data["web_update"] or data["FTL_update"]:
        JAMHAT.lights_2.off()
        JAMHAT.lights_2.yellow.blink()
    else:
        JAMHAT.lights_2.off()
        JAMHAT.lights_2.green.on()


if __name__ == "__main__":
    try:
        JAMHAT.off()
        JAMHAT.button_1.when_pressed = enable_button
        JAMHAT.button_2.when_pressed = disable_button
        JAMHAT.lights_1.red.blink()
        JAMHAT.lights_2.red.blink()
        beat.set_rate(0.2)
        while beat.true():
            # Check pihole status
            logger.debug("beat")
            check_pihole_service()
            check_pihole_version()
            beat.sleep()
    except KeyboardInterrupt:
        JAMHAT.off()
        logger.info("Stopping")
