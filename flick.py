from input_utils import *
from timing_utils import *
from log_utils import *
from pynput import keyboard
from queue import Queue, Empty
import threading
import os 
import time

userInputMQ = Queue()

def main():
    #use default debugging logging config
    debugLogs()
    debug("log config initialized")
    
    stopLight = StartStop()
    
    threading.Thread(name="flickThread", target=flickRunnable, args=(userInputMQ, stopLight), daemon=True).start()
    with keyboard.GlobalHotKeys({
        '\\': stopLight.flip,
        '-': stopLight.flip,
        '[': onAdjustTiming,
        '<ctrl>+\\': exit,
        '<ctrl>+c': exit,
        '<ctrl>+]': onConfigure,}) as l:
        l.join()

def onConfigure():
    userInputMQ.put(("PRAYER_ORB_CONFIG", getMousePosition()))
    
def onAdjustTiming():
    #timeNow is not used right now, it just shifts by 200ms
    userInputMQ.put(("TIMING_ADJUST", timeNow()))

def flickRunnable(userInputMQ, stopLight):
    #wait for configs
    prayerOrbPos = None
    while prayerOrbPos == None:
        message = userInputMQ.get()
        if message[0] == "PRAYER_ORB_CONFIG":
            prayerOrbPos = message[1]
            print("{0} set to {1}".format(message[0], message[1]))
    
    print("Config Ready")
    #wait for initial start signal
    stopLight.waitForGreen()
    
    #initialize the looping thread
    flickLoop(prayerOrbPos, stopLight, timeNow(), getMousePosition(), prayerOrbPos, userInputMQ)

def flickLoop(prayerOrbPos, stopLight, startTime, lastMousePos, orbClickLocation, userInputMQ):
    #block on the play/pause flag
    stopLight.waitForGreen()
    
    try:
        message = userInputMQ.get(False)
        if message[0] == "TIMING_ADJUST":
            startTime += 0.2
            debug("startTime is now {0}".format(startTime))
    except Empty:
        pass
    
    #kicking off new threads has horrendous drift, this variable corrects it
    driftCorrection = (timeNow() - startTime) % TICK
    
    #when moving our mouse back to the orb, randomize the location a bit
    #first conditon checks if our mouse is inactive, second condition checks to see if it's already flicking
    #if we are inactive and not already flicking, randomize
    if getMousePosition() == lastMousePos and getMousePosition() != orbClickLocation:
        orbClickLocation = (prayerOrbPos[0]+round(deviation(6)), prayerOrbPos[1]+round(deviation(6)))
        
    #kickoff next loop one tick from now
    threading.Timer(TICK-driftCorrection, flickLoop, args=(prayerOrbPos, stopLight, startTime, getMousePosition(), orbClickLocation, userInputMQ)).start()
    
    #only flick if our mouse is inactive, if it's moving, skip this iteration to allow user control
    #this allows game inputs like moving, but also clicking on another window/browser
    if getMousePosition() == orbClickLocation or getMousePosition() == lastMousePos:
        #do the flick
        click(orbClickLocation)
        wait(95,5)
        click(orbClickLocation)

if __name__ == "__main__":
    main()