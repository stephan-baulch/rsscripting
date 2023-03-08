import sched
import threading

import vision
from audio_utils import audio_ping
from input_emulation import *


def main():
    stoplight = StartStop()

    threading.Thread(target=task_controller, args=[stoplight], daemon=True).start()

    hotkey_map = {
        '<ctrl>+\\': quit,
        '<ctrl>+c': quit,
        '\\': stoplight.flip,
    }

    with keyboard.GlobalHotKeys(hotkey_map) as listener:
        listener.join()


def task_controller(stoplight):
    print(r"ready, press \ to start")
    stoplight.wait_for_green()

    vision.init_vision()
    screenshot = vision.get_screenshot()
    inventory_loc = vision.locate_inventory(screenshot)
    prayer_orb_loc = vision.locate_prayer_orb(screenshot)

    inv = vision.crop_inventory(inventory_loc, screenshot)
    absorbs = vision.find_all_absorbs(inv)
    overloads = vision.find_all_overloads(inv)
    loc_orb_loc = vision.find_locator_orb(inv)

    for i in range(5):
        for j in range(4):
            click_inventory(*absorbs[i], inventory_loc)
            wait_ticks(4, 300)
        if i == 3:
            click_inventory(*overloads[0], inventory_loc)
            wait_ticks(4, 300)

    for i in range(15):
        click_inventory(loc_orb_loc[0], loc_orb_loc[1], inventory_loc)
        wait_ticks(1, 50)

    s = sched.scheduler(time.time, time.sleep)
    s.enter(0, 0, flick_regen_loop, argument=(s, stoplight, prayer_orb_loc))
    # this needs to run exactly 5 minutes after the first overload is clicked
    s.enter(285, 0, refresh_pots_loop, argument=(s, stoplight, inventory_loc, prayer_orb_loc))
    s.run()


def flick_regen_loop(scheduler, stoplight, prayer_orb_loc):
    scheduler.enter(55, 0, flick_regen_loop, argument=(scheduler, stoplight, prayer_orb_loc))

    flick(xy_near(prayer_orb_loc, 5), 300)


def refresh_pots_loop(scheduler, stoplight, inventory_loc, prayer_orb_loc):
    scheduler.enter(302, 0, refresh_pots_loop, argument=(scheduler, stoplight, inventory_loc, prayer_orb_loc))
    audio_ping()

    screenshot = vision.get_screenshot()
    inv = vision.crop_inventory(inventory_loc, screenshot)

    absorbs = vision.find_all_absorbs(inv)
    overloads = vision.find_all_overloads(inv)

    flick(xy_near(prayer_orb_loc, 5), 300)
    wait(500, 50)
    click_inventory(*overloads[0], inventory_loc)
    wait_ticks(4, 300)
    click_inventory(*absorbs[0], inventory_loc)
    wait_ticks(4, 300)
    click_inventory(*absorbs[1], inventory_loc)
    wait_ticks(4, 300)
    click_inventory(*absorbs[2], inventory_loc)


if __name__ == "__main__":
    main()
