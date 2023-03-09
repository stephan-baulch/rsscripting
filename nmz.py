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
    print(r"Ready, press \ to start")
    stoplight.wait_for_green()

    vision.init_vision()
    screenshot = vision.get_screenshot()
    inventory_loc = vision.locate_inventory(screenshot)
    prayer_orb_loc = vision.locate_prayer_orb(screenshot)

    inv = vision.crop_inventory(inventory_loc, screenshot)
    absorbs = vision.find_all_absorbs(inv)
    overloads = vision.find_all_overloads(inv)
    loc_orb_loc = vision.find_locator_orb(inv)

    s = sched.scheduler(time.time, time.sleep)
    for i in range(5):
        for _ in range(4):
            click_inventory(*absorbs[i], inventory_loc)
            wait_ticks(4, 300)
        if i == 2:
            click_inventory(*overloads[0], inventory_loc)
            s.enter(302, 0, refresh_pots_loop, argument=(s, stoplight, inventory_loc, prayer_orb_loc))
            wait_ticks(4, 300)
        if i == 3:
            for _ in range(15):
                click_inventory(loc_orb_loc[0], loc_orb_loc[1], inventory_loc)
                wait_ticks(1, 50)

    # s.enter(62, 0, refresh_pots_loop, argument=(s, stoplight, inventory_loc, prayer_orb_loc))
    s.enter(0, 0, flick_regen_loop, argument=(s, stoplight, inventory_loc, prayer_orb_loc, loc_orb_loc))
    s.run()


def flick_regen_loop(scheduler, stoplight, inventory_loc, prayer_orb_loc, loc_orb_loc):
    stoplight.wait_for_green()

    screenshot = vision.get_screenshot()

    if vision.check_nmz_exit(screenshot, prayer_orb_loc):
        print(f"{time.asctime()}: Full hp detected, exiting")
        stoplight.red()
        del scheduler
        exit()

    scheduler.enter(55, 0, flick_regen_loop, argument=(scheduler, stoplight, inventory_loc, prayer_orb_loc, loc_orb_loc))

    flick(xy_near(prayer_orb_loc, 5), 1000)

    wait_ticks(2, 100)
    screenshot = vision.get_screenshot()
    if vision.check_flick_failure(screenshot, prayer_orb_loc):
        print(f"{time.asctime()}: Prayer orb flick failure detected")
        click(xy_near(prayer_orb_loc, 5))
        wait(500, 50)
        if vision.check_hp_over_1(screenshot, prayer_orb_loc):
            print(f"{time.asctime()}: HP regen detected")
            for i in range(3):
                click_inventory(loc_orb_loc[0], loc_orb_loc[1], inventory_loc)
                wait_ticks(1, 50)


def refresh_pots_loop(scheduler, stoplight, inventory_loc, prayer_orb_loc):
    scheduler.enter(303, 0, refresh_pots_loop, argument=(scheduler, stoplight, inventory_loc, prayer_orb_loc))
    audio_ping()

    screenshot = vision.get_screenshot()

    inv = vision.crop_inventory(inventory_loc, screenshot)

    absorbs = vision.find_all_absorbs(inv)
    overloads = vision.find_all_overloads(inv)

    if vision.check_nmz_exit(screenshot, prayer_orb_loc) or not overloads or len(absorbs) < 3:
        print(f"{time.asctime()}: Full hp detected, exiting")
        stoplight.red()
        del scheduler
        exit()

    flick(xy_near(prayer_orb_loc, 5), 1000)
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
