from pynput import mouse, keyboard
import threading
import queue
import time
import random

m = mouse.Controller()
kb = keyboard.Controller()

nextRock = 2

rock1Position = None
rock2Position = None
rock3Position = None

grinderPosition = None
returnPosition = None

maxVariation = 5

def click(target):
    global maxVariation
    randomizedX = random.gauss(target[0], 2)
    randomizedY = random.gauss(target[1], 2)

    if randomizedX > target[0] + maxVariation:
        randomizedX = target[0] + maxVariation
    elif randomizedX < target[0] - maxVariation:
        randomizedX = target[0] - maxVariation
    if randomizedY > target[1] + maxVariation:
        randomizedY = target[1] + maxVariation
    elif randomizedY < target[1] - maxVariation:
        randomizedY = target[1] - maxVariation
        
    randomizedTarget = (randomizedX, randomizedY)
    
    print("target: {0}", target)
    print("randomizedTarget: {0}", randomizedTarget)
    
    m.position = randomizedTarget
    wait(0.05, 0.01)
    m.press(mouse.Button.left)
    wait(0.05, 0.01)
    m.position = randomizedTarget
    m.release(mouse.Button.left)
    
def wait(duration, maxDelta):
    waitTime = random.gauss(duration, maxDelta/2)
    
    #keep the random number within max delta
    if waitTime > duration + maxDelta:
        waitTime = duration + maxDelta
    elif waitTime < duration - maxDelta:
        waitTime = duration - maxDelta
        
    time.sleep(waitTime)
    
def on_configure():
    global rock1Position
    global rock2Position
    global rock3Position

    global grinderPosition
    global returnPosition
    
    if rock1Position == None:
        rock1Position = m.position
        print('Configured rock 1: {0}'.format(rock1Position))
        return

    if rock2Position == None:
        rock2Position = m.position
        print('Configured rock 2: {0}'.format(rock2Position))
        return

    if rock3Position == None:
        rock3Position = m.position
        print('Configured rock 3: {0}'.format(rock3Position))
        return
        
    if grinderPosition == None:
        grinderPosition = m.position
        print('Configured grinder 1: {0}'.format(grinderPosition))
        return
        
    if returnPosition == None:
        returnPosition = m.position
        print('Configured return 1: {0}'.format(returnPosition))
        return
        
def on_next_rock():
    global nextRock
    if nextRock == 1:
        click(rock1Position)
        nextRock = 2
        return
    
    if nextRock == 2:
        click(rock2Position)
        nextRock = 3
        return

    click(rock3Position)
    nextRock = 1
    
def on_deposit():
    global nextRock
    click(grinderPosition)
    wait(8, 0.5)
    click(returnPosition)
    nextRock = 2
        
hotkeyMap = {
    '<ctrl>+\\' : on_configure,
    '<ctrl>+=' : quit,
    '\'' : on_next_rock,
    '-' : on_deposit,
}

with keyboard.GlobalHotKeys(hotkeyMap) as listener:
    listener.join()