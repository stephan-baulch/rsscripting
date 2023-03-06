from input_emulation import *
from utils import *
from user_interface import *
from pynput import keyboard
from queue import Queue
import threading
import os
import time
from pprint import pprint

configQueue = Queue()

def main():
    stopLight = StartStop()
    
    threading.Thread(name="alchThread", target=bStaffRunnable, args=(configQueue, stopLight), daemon=True).start()
    with keyboard.GlobalHotKeys({
        '\\': stopLight.flip,
        '<ctrl>+\\': exit,
        '<ctrl>+c': exit,
        '<ctrl>+]': onConfigure,}) as l:
        l.join()

def onConfigure():
    configQueue.put(("BSTAFF_CONFIG", getMousePosition()))

def bStaffRunnable(configQueue, stopLight):
    clickPositions = {}
    
    bstaffCount = int(dialog_input("How many battlestaffs?"))

    #wait for configs
    message = configQueue.get()
    clickPositions["bank"] = message[1]
    print("{0} set to {1}".format("bank", message[1]))
    
    message = configQueue.get()
    clickPositions["deposit_all"] = message[1]
    print("{0} set to {1}".format("deposit_all", message[1]))
    
    message = configQueue.get()
    clickPositions["withdraw"]  = message[1]
    print("{0} set to {1}".format("withdraw", message[1]))
    
    message = configQueue.get()
    clickPositions["inventory_craft"]  = message[1]
    print("{0} set to {1}".format("inventory_craft", message[1]))
    
    print("READY TO START")
    
    #wait for initial start signal
    stopLight.wait_for_green()
    
    #initialize the looping thread
    bStaffThreadLoop(clickPositions, stopLight, 0, bstaffCount)

def bStaffThreadLoop(clickPositions, stopLight, iterations, quantity):
    #block on wait signal
    stopLight.wait_for_green()
    
    if iterations >= quantity-15:
        quit()
        
    #kickoff next loop
    threading.Timer(28+deviation(1000)/1000, bStaffThreadLoop, args=(clickPositions, stopLight, iterations+14, quantity)).start()
    
    #open the bank
    clickWithDelay(clickPositions["bank"], 80, 3)
    
    wait_ticks(3, 10)
    stopLight.wait_for_green()
    #deposit bstaffs
    click(clickPositions["deposit_all"],3)
    
    wait_ticks(2, 10)
    stopLight.wait_for_green()
    #withdraw orbs
    click(clickPositions["withdraw"],3)
    
    wait(350,25)
    stopLight.wait_for_green()
    #withdraw bstaffs
    click((clickPositions["withdraw"][0]+43,clickPositions['withdraw'][1]),3)
    
    wait_ticks(2, 10)
    stopLight.wait_for_green()
    #close bank
    esc()
    
    wait_ticks(2, 25)
    stopLight.wait_for_green()
    #click orb
    click(clickPositions["inventory_craft"],3)
    
    wait(350,25)
    stopLight.wait_for_green()
    #click bstaff
    click((clickPositions["inventory_craft"][0]+42,clickPositions['inventory_craft'][1]),3)
    
    wait_ticks(3, 10)
    stopLight.wait_for_green()
    #confirm craft
    spacebar()

if __name__ == "__main__":
    main()