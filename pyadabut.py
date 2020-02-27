#!/usr/bin/python3
import requests
from cronus import beat
from gpiozero import Button, PWMOutputDevice
from loguru import logger

from pyjamhole import get_web_password

URL = "http://localhost/admin/api.php"
DISABLE_TIME = 300
TIMEOUT_TIME = 5


def show_screen():
    global screen_timeout
    logger.info("Show Screen")
    screen_timeout = TIMEOUT_TIME


def hide_screen():
    global screen_timeout
    logger.info("Hide Screen")
    screen_timeout = 0


def pause_pihole():
    logger.info("disable button pressed")
    r = requests.get(URL, params={"disable": DISABLE_TIME, "auth": get_web_password()})


def resume_pihole():
    logger.info("enable button pressed")
    r = requests.get(URL, params={"enable": True, "auth": get_web_password()})


if __name__ == "__main__":
    display = PWMOutputDevice(18)
    button_1 = Button(17)
    button_2 = Button(22)
    button_3 = Button(23)
    button_4 = Button(27)

    button_1.when_pressed = show_screen
    button_2.when_pressed = hide_screen
    button_3.when_pressed = pause_pihole
    button_4.when_pressed = resume_pihole
    beat.set_rate(1)
    screen_timeout = TIMEOUT_TIME
    while beat.true():
        if screen_timeout > 0:
            display.on()
            screen_timeout -= 1
        else:
            display.off()
        beat.sleep()
