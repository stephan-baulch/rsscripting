from dataclasses import dataclass
from threading import Event, Timer
import time
import random
from typing import Tuple, Callable
import queue

TICK = 0.6


class StartStop:
    """
    A thread-safe stoplight used for play/pause
    Communicates between the keyboard event listener thread and the controller thread
    """
    stopEvent = Event()

    def flip(self):
        if self.stopEvent.is_set():
            self.red()
        else:
            self.green()

    def green(self):
        print("Green Light")
        self.stopEvent.set()

    def red(self):
        print("Red Light")
        self.stopEvent.clear()

    def wait_for_green(self):
        self.stopEvent.wait()


def wait_ticks(ticks: int, max_dev: int = 0) -> None:
    """ deviation is measured in milliseconds """
    time.sleep(ticks * TICK + deviation(max_dev) / 1000)


def wait(wait_time: int, max_dev=0) -> None:
    """ wait_time and deviation are in milliseconds """
    time.sleep((wait_time + deviation(max_dev)) / 1000)


def deviation(max_dev: int) -> int:
    dev = round(random.gauss(0, max_dev / 2))
    if dev > max_dev or dev < -max_dev:
        dev = random.randint(-max_dev, max_dev)
    return dev


def xy_near(coordinate: Tuple[int, int], max_dev: int) -> Tuple[int, int]:
    """ Returns a random xy coordinate within {max_dev} of {coordinate} """
    return coordinate[0] + deviation(max_dev), coordinate[1] + deviation(max_dev)
