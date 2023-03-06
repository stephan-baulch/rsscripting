import cv2 as opencv
import dxcam
import threading
import time

# based on pyautogui/pyscreeze's implementation
# https://github.com/asweigart/pyscreeze/blob/master/pyscreeze/__init__.py
# template matching explanation
# https://stackoverflow.com/questions/58158129/understanding-and-evaluating-template-matching-methods

# candidates for rapid screenshotting: MSS and DXcam, both are designed for high speed captures
# https://python-mss.readthedocs.io/index.html
# https://github.com/ra1nty/DXcam seems to be designed for high rate of screenshotting

# this whole class needs to be refactored into an instance that works well with the greater multi-threaded script
_camera = None
_window_name = "CV Output"


# main is used for visually debugging these methods
def main():
    init_vision()

    while True:
        screenshot = _camera.grab()

        inv_loc = locate_inventory(screenshot)
        for i in range(4):
            for j in range(7):
                opencv.circle(screenshot, (int(inv_loc[0] + i * 127 / 3), int(inv_loc[1] + j * 217 / 6)), 15,
                              (255, 0, 255))

        pray_orb_loc = locate_prayer_orb(screenshot)
        opencv.circle(screenshot, pray_orb_loc, 15, (255, 255, 0))

        if opencv.waitKey(1000) == 27:
            release_vision()
            return


# returns coordinate in x,y format
def locate_inventory(template):
    match_image = _open_image(r"res\InventoryMatcher.png")
    result = opencv.matchTemplate(match_image, template, opencv.TM_SQDIFF)
    val, _, loc, _ = opencv.minMaxLoc(result)
    return (loc[0] + 48, loc[1] + 55)


# returns coordinate in x,y format
def locate_prayer_orb(template):
    match_image = _open_image(r"res\PrayerOrbMatcher.png")
    result = opencv.matchTemplate(match_image, template, opencv.TM_SQDIFF)
    val, _, loc, _ = opencv.minMaxLoc(result)
    return (loc[0] + 35, loc[1] + 64)


def screenshot():
    # this can break because this will return None if called multiple times within the same frame
    return _camera.grab()


def init_vision(gray=False):
    global _camera
    global _window_name

    opencv.namedWindow(_window_name)
    opencv.moveWindow(_window_name, 1920, 0)

    if gray:
        _camera = dxcam.create(output_color="GRAY")
    else:
        _camera = dxcam.create(output_color="BGR")


# the first thread that calls pollKey or waitKey has exclusive control over the window updates
# which means this method will only work to display a static image for debugging
def init_window_thread(_window_name, screenshot):
    threading.Thread(target=_window_thread_loop(_window_name, screenshot)).start()


def _window_thread_loop(_window_name, screenshot):
    opencv.imshow(_window_name, screenshot)
    while True:
        if opencv.waitKey(1000) == 27:
            opencv.destroyWindow(_window_name)
            return


def release_vision():
    _camera.release()
    opencv.destroyAllWindows()


def _open_image(filename, gray=False):
    if gray:
        return opencv.imread(filename, opencv.IMREAD_GRAYSCALE)
    else:
        # this strips the alpha channel and returns a 3d numpy array in BGR format
        return opencv.imread(filename, opencv.IMREAD_COLOR)


if __name__ == "__main__":
    main()
