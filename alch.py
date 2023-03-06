from input_emulation import *
from utils import *
from user_interface import *
from pynput import keyboard
from queue import Queue
import threading
import os 
import time

configQueue = Queue()

def main():
    stopLight = StartStop()
    
    threading.Thread(name="alchThread", target=alchRunnable, args=(configQueue, stopLight), daemon=True).start()
    with keyboard.GlobalHotKeys({
        '\\': stopLight.flip,
        '<ctrl>+\\': exit,
        '<ctrl>+c': exit,
        '<ctrl>+]': onConfigure,}) as l:
        l.join()

def onConfigure():
    configQueue.put(("ALCH_CONFIG", getMousePosition()))

def alchRunnable(configQueue, stopLight):
    
    maxIterations = int(dialog_input("How many battlestaffs?"))

    #wait for configs
    alchClickPos = None
    while alchClickPos == None:
        message = configQueue.get()
        if message[0] == "ALCH_CONFIG":
            alchClickPos = message[1]
            print("{0} set to {1}".format(message[0], message[1]))
            
    
    #wait for initial start signal
    stopLight.wait_for_green()
    
    #initialize the looping thread
    alchThreadLoop(alchClickPos, stopLight, 0, maxIterations)

def alchThreadLoop(alchClickPos, stopLight, iterations, quantity):
    #block on wait signal
    stopLight.wait_for_green()
    
    if iterations == quantity:
        quit()
        
    #kickoff next loop
    threading.Timer(7*TICK , alchThreadLoop, args=(alchClickPos, stopLight, iterations+1, quantity)).start()
    
    #do the alch
    click(alchClickPos)
    wait_ticks(2)
    click(alchClickPos)

if __name__ == "__main__":
    main()