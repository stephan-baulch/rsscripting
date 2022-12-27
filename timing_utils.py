from threading import Event
from time import sleep, time
import random

TICK = 0.6

class StartStop:
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
        
    def waitForGreen(self):
        self.stopEvent.wait()
       
#deviation is measured in milliseconds
def ticks(ticks, maxDev = 0):
    sleep(ticks*TICK + deviation(maxDev)/1000)

#time and deviation are in milliseconds
def wait(time, maxDev = 0):
    sleep(time/1000 + deviation(maxDev)/1000)
    
def deviation(maxDev):
    dev = random.gauss(0, maxDev/2)
    if dev > maxDev or dev < -maxDev:
        dev = random.randint(-maxDev, maxDev)
    return dev
    
def timeNow():
    return time()