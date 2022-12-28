from pynput import mouse, keyboard
from audio_utils import bidoop
import threading
import queue
import time
import random
from pandas import DataFrame

m = mouse.Controller()
kb = keyboard.Controller()

tick = 0.6
prayerOrbLocation = None
inventory = None
ovlDosesDrank = 1
absDosesDrank = 0

def calculateInventoryGrid(topLeft, bottomRight):
    xoffset = (bottomRight[0]-topLeft[0])/3
    yoffset = (bottomRight[1]-topLeft[1])/6
    inventory = [[None for x in range(4)] for y in range(7)]
    
    for i in range(7):
        for j in range(4):
            inventory[i][j] = (round(topLeft[0] + j * xoffset), round(topLeft[1] + i * yoffset))
            
    return inventory

def clickInventory(x,y):
    global inventory
    xPixel = bellCurve(inventory[y][x][0], 3) 
    yPixel = bellCurve(inventory[y][x][1], 3) 
    click((xPixel, yPixel))
    
def drinkOvl():
    global ovlDosesDrank
    if ovlDosesDrank in range(0,4):
        clickInventory(0,0)
        ovlDosesDrank += 1
    elif ovlDosesDrank in range(4,8):
        clickInventory(1,0)
        ovlDosesDrank += 1
    elif ovlDosesDrank in range(8,12):
        clickInventory(2,0)
        ovlDosesDrank += 1
    elif ovlDosesDrank in range(12,16):
        clickInventory(3,0)
        ovlDosesDrank += 1
    elif ovlDosesDrank in range(16,20):
        clickInventory(2,6)
        ovlDosesDrank += 1

def drinkAbs():
    global absDosesDrank
    if absDosesDrank in range(0,4):
        clickInventory(0,1)
        absDosesDrank += 1
    elif absDosesDrank in range(4,8):
        clickInventory(1,1)
        absDosesDrank += 1
    elif absDosesDrank in range(8,12):
        clickInventory(2,1)
        absDosesDrank += 1
    elif absDosesDrank in range(12,16):
        clickInventory(3,1)
        absDosesDrank += 1
    elif absDosesDrank in range(16,20):
        clickInventory(0,2)
        absDosesDrank += 1
    elif absDosesDrank in range(20,24):
        clickInventory(1,2)
        absDosesDrank += 1
    elif absDosesDrank in range(24,28):
        clickInventory(2,2)
        absDosesDrank += 1
    elif absDosesDrank in range(28,32):
        clickInventory(3,2)
        absDosesDrank += 1
    elif absDosesDrank in range(32,36):
        clickInventory(0,3)
        absDosesDrank += 1
    elif absDosesDrank in range(36,40):
        clickInventory(0,3)
        absDosesDrank += 1
    elif absDosesDrank in range(40,44):
        clickInventory(1,3)
        absDosesDrank += 1
    elif absDosesDrank in range(44,48):
        clickInventory(2,3)
        absDosesDrank += 1
    elif absDosesDrank in range(48,52):
        clickInventory(3,3)
        absDosesDrank += 1
    elif absDosesDrank in range(52,56):
        clickInventory(0,4)
        absDosesDrank += 1
    elif absDosesDrank in range(56,60):
        clickInventory(1,4)
        absDosesDrank += 1
    elif absDosesDrank in range(60,64):
        clickInventory(2,4)
        absDosesDrank += 1
    elif absDosesDrank in range(64,68):
        clickInventory(3,4)
        absDosesDrank += 1
    elif absDosesDrank in range(68,72):
        clickInventory(0,5)
        absDosesDrank += 1
    elif absDosesDrank in range(72,76):
        clickInventory(1,5)
        absDosesDrank += 1
    elif absDosesDrank in range(76,80):
        clickInventory(2,5)
        absDosesDrank += 1
    elif absDosesDrank in range(80,84):
        clickInventory(3,5)
        absDosesDrank += 1
    elif absDosesDrank in range(84,88):
        clickInventory(0,6)
        absDosesDrank += 1
    elif absDosesDrank in range(88,92):
        clickInventory(1,6)
        absDosesDrank += 1
    elif absDosesDrank in range(92,96):
        clickInventory(2,6)
        absDosesDrank += 1

def click(target):
    m.position = target
    wait(0.02, 0.01)
    m.press(mouse.Button.left)
    wait(0.02, 0.01)
    m.position = target
    m.release(mouse.Button.left)
   
def bellCurve(avg, delta):
    randNum = random.gauss(avg, delta/2)
    
    if randNum > avg + delta:
        randNum = avg + delta
    elif randNum < avg - delta:
        randNum = avg - delta

    return randNum

def wait(duration, maxDelta):        
    time.sleep(bellCurve(duration, maxDelta))

def flick():
    click(prayerOrbLocation)
    wait(0.06, 0.01)
    click(prayerOrbLocation)

def flickRegenLoop():    
    regenTimer = threading.Timer(90*tick, flickRegenLoop)
    regenTimer.daemon = True
    regenTimer.start()
    
    flick()
    
def refreshPotsLoop():
    refreshPotsTimer = threading.Timer(505*tick, refreshPotsLoop)
    refreshPotsTimer.daemon = True
    refreshPotsTimer.start()
    
    bidoop()
    
    wait(tick*4, tick/2)
    drinkOvl()
    wait(tick*4, tick/2)
    drinkAbs()
    wait(tick*4, tick/2)
    drinkAbs()
    wait(tick*4, tick/2)
    drinkAbs()
    wait(tick*4, tick/2)

def runRefreshPots():
    pauseEvent.wait()
    
    refreshPotsTimer = threading.Timer(510*tick, refreshPotsLoop)
    refreshPotsTimer.daemon = True
    refreshPotsTimer.start()
    
def runRegenFlicker():
    #wait for start
    pauseEvent.wait()
    #gogogo
    flickRegenLoop()
    
def on_configure():
    global prayerOrbLocation
    global inventory
    
    if prayerOrbLocation == None:
        prayerOrbLocation = m.position
        print('Configured prayer orb: {0}'.format(prayerOrbLocation))
        return

    if inventory == None:
        topLeftInventory = m.position
        inventory = calculateInventoryGrid(topLeftInventory, (topLeftInventory[0]+126,topLeftInventory[1]+217))
        
        print("Inventory coordinates: \n{0}".format(DataFrame(inventory)))
        return
        

def on_startstop():
    if pauseEvent.isSet():
        pauseEvent.clear()
        print('stop')
    else:
        pauseEvent.set()
        print('go')

hotkeyMap = {
    '<ctrl>+\\' : on_configure,
    '<ctrl>+=' : quit,
    '\'' : on_startstop,
}

pauseEvent = threading.Event()
threading.Thread(target=runRegenFlicker, daemon=True).start()
threading.Thread(target=runRefreshPots, daemon=True).start()

with keyboard.GlobalHotKeys(hotkeyMap) as listener:
    listener.join()
    

    