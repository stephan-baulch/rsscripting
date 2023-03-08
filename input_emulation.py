from pynput import keyboard, mouse
from utils import *
import random

_m = mouse.Controller()
_k = keyboard.Controller()


def click(target, max_dev=0):
    click_position = xy_near(target, max_dev)

    _m.position = click_position
    _m.press(mouse.Button.left)
    wait(15, 5)
    _m.position = click_position
    _m.release(mouse.Button.left)


def flick(loc, delay=85):
    click(loc)
    wait(delay, 5)
    click(loc)


def click_inventory(x, y, inventory_loc):
    x_pixel = round(inventory_loc[0] + x * 127 / 3)
    y_pixel = round(inventory_loc[1] + y * 217 / 6)
    click((x_pixel, y_pixel), 5)


def click_with_delay(target, delay, max_dev=0):
    click_position = target
    if max_dev != 0:
        click_position = (click_position[0] + deviation(max_dev), click_position[1] + deviation(max_dev))
    _m.position = click_position
    wait(delay)
    click(click_position)


def spacebar():
    _k.press(keyboard.Key.space)
    wait(15, 5)
    _k.release(keyboard.Key.space)


def esc():
    _k.press(keyboard.Key.esc)
    wait(15, 5)
    _k.release(keyboard.Key.esc)


def get_mouse_position():
    return _m.position


def deviation(max_dev):
    dev = random.gauss(0, max_dev / 2)
    if dev > max_dev or dev < -max_dev:
        dev = random.randint(-max_dev, max_dev)
    return dev
