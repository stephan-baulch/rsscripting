from pynput import keyboard, mouse
from utils import *
import random

#custom tkinter for input boxes

m = mouse.Controller()
k = keyboard.Controller()

def click(target, maxDev=0):
    clickPosition = target
    if maxDev != 0:
        clickPosition = (clickPosition[0]+deviation(maxDev),clickPosition[1]+deviation(maxDev))
    
    m.position = clickPosition
    m.press(mouse.Button.left)
    wait(15, 5)
    m.position = clickPosition
    m.release(mouse.Button.left)
    
def clickWithDelay(target, delay, maxDev=0):
    clickPosition = target
    if maxDev != 0:
        clickPosition = (clickPosition[0]+deviation(maxDev),clickPosition[1]+deviation(maxDev))
    m.position = clickPosition
    wait(delay)
    click(clickPosition)
    
def spacebar():
    k.press(keyboard.Key.space)
    k.release(keyboard.Key.space)
    
def esc():
    k.press(keyboard.Key.esc)
    k.release(keyboard.Key.esc)
    
def getMousePosition():
    return m.position
    
def deviation(maxDev):        
    dev = random.gauss(0, maxDev/2)
    if dev > maxDev or dev < -maxDev:
        dev = random.randint(-maxDev, maxDev)
    return dev