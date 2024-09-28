import vision
import cv2
import threading

from utils import StartStop
from input_emulation import *

locations = {
    'feet_loc': None,
    'bank_loc': None,
    'cast_loc': None,
    'gsweed_loc': None,
    'sand_loc': None,
    'inv_loc': None,
}

stoplight = StartStop()

def main():
    #threading.Thread(target=task_controller, args=[stoplight], daemon=True).start()

    hotkeyMap = {
        '\\': stoplight.flip,
        '<ctrl>+\\': exit,
        '<ctrl>+c': exit,
        ']': onConfigure,
    }
    
    vision.init_vision()
    
    threading.Thread(target=loop, daemon=True).start()
    
    print('Press ] once bank is visible')
    with keyboard.GlobalHotKeys(hotkeyMap) as l:
        l.join()

def debugLocations():
    screenshot = vision.get_screenshot()
    for key, loc in locations.items():
        cv2.circle(screenshot, loc, 15, (255, 255, 0))

    window_name = "CV Output"
    cv2.namedWindow(window_name)
    cv2.moveWindow(window_name, 2160, 0)
    cv2.imshow(window_name, screenshot)

    while True:
        if cv2.waitKey(1000) == 27:
            release_vision()
            return
            
def onConfigure():
    if locations['gsweed_loc'] == None:
        screenshot = vision.get_screenshot()
        locations['inv_loc'] = vision.locate_inventory_from_bank(screenshot)
        locations['gsweed_loc'] = vision.locate_gsweed(screenshot)
        locations['sand_loc'] = (locations['gsweed_loc'][0]+47, locations['gsweed_loc'][1])
        #print('Configured gsweed: {0}'.format(locations['gsweed_loc']))
        #print('Configured sand: {0}'.format(locations['sand_loc']))
        #print('Configured inventory: {0}'.format(locations['inv_loc']))
        print('Press ] once spellbook is visible')
        return
        
    if locations['cast_loc'] == None:
        screenshot = vision.get_screenshot()
        locations['cast_loc'] = vision.locate_superglass(screenshot)
        #print('Configured sgm cast: {0}'.format(locations['cast_loc']))
        print('Press ] with cursor on feet')
        return
        
    if locations['feet_loc'] == None:
        locations['feet_loc'] = get_mouse_position()
        #print('Configured feet: {0}'.format(locations['feet_loc']))
        print('Press ] with cursor on bank')
        return

    if locations['bank_loc'] == None:
        locations['bank_loc'] = get_mouse_position()
        #print('Configured bank: {0}'.format(locations['bank_loc']))
    
    print('press \ to start, inventory should be full of gsweed and sand')
    # uncomment this to debug click locations
    # debugLocations()
    
def loop():
    stoplight.wait_for_green()
    click(locations['cast_loc'], 3)
    wait(3000, 499)
    stoplight.wait_for_green()
    click_with_delay(locations['bank_loc'], 500, 15)
    wait(1800, 391)
    stoplight.wait_for_green()
    click_inventory(0,0,locations['inv_loc'])
    wait(900,205)
    stoplight.wait_for_green()
    initial_gsweed = xy_near(locations['gsweed_loc'], 5)
    click(initial_gsweed)
    wait(350,66)
    stoplight.wait_for_green()
    click(initial_gsweed)
    wait(510,154)
    stoplight.wait_for_green()
    click(locations['sand_loc'], 5)
    wait(740,220)
    stoplight.wait_for_green()
    esc()
    wait(1121,301)
    stoplight.wait_for_green()
    loop()

if __name__ == "__main__":
    main()
