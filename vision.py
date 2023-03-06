import cv2 as opencv
import dxcam
from threading import Thread
import time

# based on pyautogui/pyscreeze's implementation
# https://github.com/asweigart/pyscreeze/blob/master/pyscreeze/__init__.py
# template matching explanation
# https://stackoverflow.com/questions/58158129/understanding-and-evaluating-template-matching-methods

# candidates for rapid screenshotting: MSS and DXcam, both are designed for high speed captures
# https://python-mss.readthedocs.io/index.html
# https://github.com/ra1nty/DXcam seems to be designed for high rate of screenshotting

_camera = None
_window_name = "CV Output"


def main():
    init_vision()
    while True:
        screenshot = _camera.grab()
        loc = locate_inventory(screenshot)
        bottom_right = (loc[0] + 127, loc[1] + 217)
        for i in range(4):
            for j in range(7):
                opencv.circle(screenshot, (int(loc[0]+i*127/3), int(loc[1]+j*217/6)), 15, (255,0,255))
        opencv.imshow(_window_name, screenshot)
        if opencv.waitKey(1) == 27:
            return

# returns coordinate in x,y format
def locate_inventory(template):

    match_image = _open_image(r"res\InventoryMatcher.png")
    result = opencv.matchTemplate(match_image, template, opencv.TM_SQDIFF)
    val, _, loc, _ = opencv.minMaxLoc(result)
    return (loc[0] + 48, loc[1] + 55)


def locate_prayer_orb():
    match_image = _open_image(r"res\PrayOrbMatcher.png")
    template_image = _camera.grab()
    result = opencv.matchTemplate(match_image, template_image, opencv.TM_SQDIFF)
    val, _, loc, _ = opencv.minMaxLoc(result)
    print(f"prayer orb is at {loc}, value is {val}")
    bottom_right = (loc[0] + match_image.shape[0], loc[1] + match_image.shape[1])
    opencv.rectangle(template_image, loc, bottom_right, (0,255,0))
    opencv.imshow(_window_name, template_image)
    return loc


def init_vision(gray=False):
    global _camera
    global _window_name

    opencv.namedWindow(_window_name)
    opencv.moveWindow(_window_name, 1920, 0)
    #Thread(target=_vision_thread_loop, daemon=True).start

    if gray:
        _camera = dxcam.create(output_color="GRAY")
    else:
        _camera = dxcam.create(output_color="BGR")


def _vision_thread_loop():
    if opencv.pollKey() == 27:
        return
    time.sleep(1)


def release_vision():
    _camera.release()
    opencv.destroyWindow(_window_name)


def _open_image(filename, gray=False):
    if gray:
        return opencv.imread(filename, opencv.IMREAD_GRAYSCALE)
    else:
        # this strips the alpha channel and returns a 3d numpy array in BGR format
        return opencv.imread(filename, opencv.IMREAD_COLOR)


if __name__ == "__main__":
    main()