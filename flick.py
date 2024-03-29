from input_emulation import *
from utils import *
import logging as log
from pynput import keyboard
from queue import Queue, Empty
import threading
import vision
from functools import partial
import sched


def main():
    log.basicConfig(
        filename='log.txt',
        filemode='w',
        level=log.DEBUG,
        format='%(asctime)s: %(message)s')
    log.info("log config initialized")

    user_input_mq = Queue()
    stoplight = StartStop()

    # this is ugly, I don't like it, vision should be refactored into something instanced
    vision.init_vision()
    prayer_orb_pos = vision.locate_prayer_orb(vision.get_screenshot())
    vision.release_vision()

    threading.Thread(
        name="flickThread",
        target=flick_runnable,
        args=(user_input_mq, stoplight, prayer_orb_pos),
        daemon=True
    ).start()

    with keyboard.GlobalHotKeys({
        '\\': stoplight.flip,
        '-': stoplight.flip,
        '[': partial(on_adjust_timing, user_input_mq),
        '<ctrl>+\\': exit,
        '<ctrl>+c': exit,
    }) as listener:
        listener.join()


def on_adjust_timing(user_input_mq):
    # time is ignored for now, it just shifts by 1/3 of a tick
    user_input_mq.put(("TIMING_ADJUST", time.time()))


def flick_runnable(user_input_mq, stoplight, prayer_orb_pos):
    s = sched.scheduler(time.time, time.sleep)
    s.enter(0, 0, flick_loop, argument=(s, prayer_orb_pos, stoplight, time.time(), get_mouse_position(), prayer_orb_pos, user_input_mq))
    s.run()


def flick_loop(scheduler, prayer_orb_pos, stoplight, start_time, last_mouse_pos, click_loc, user_input_mq):
    # block on the play/pause flag
    stoplight.wait_for_green()

    try:
        message = user_input_mq.get(False)
        if message[0] == "TIMING_ADJUST":
            start_time += 0.2
            log.debug(f"startTime is now {start_time}")
    except Empty:
        pass

    # kicking off new threads has horrendous drift, this corrects it
    next_time = time.time() + TICK - (time.time() - start_time) % TICK

    # when moving our mouse back to the orb, randomize the location a bit
    # first condition checks if our mouse is inactive, second condition checks to see if it's already flicking
    # if we are inactive and not already flicking, randomize\
    if get_mouse_position() == last_mouse_pos and get_mouse_position() != click_loc:
        click_loc = (prayer_orb_pos[0] + round(deviation(6)), prayer_orb_pos[1] + round(deviation(6)))

    scheduler.enterabs(next_time, 0, flick_loop,
                       argument=(scheduler,
                                 prayer_orb_pos,
                                 stoplight,
                                 start_time,
                                 get_mouse_position(),
                                 click_loc,
                                 user_input_mq))

    # only flick if our mouse is inactive, if it's moving, skip this iteration to allow user control
    # this allows game inputs like moving, but also clicking on another window/browser
    if get_mouse_position() == click_loc or get_mouse_position() == last_mouse_pos:
        flick(click_loc)


if __name__ == "__main__":
    main()
