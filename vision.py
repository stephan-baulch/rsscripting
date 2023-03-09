import cv2 as opencv
import dxcam
import threading
import utils

# based on pyautogui/pyscreeze's implementation
# https://github.com/asweigart/pyscreeze/blob/master/pyscreeze/__init__.py
# template matching explanation
# https://stackoverflow.com/questions/58158129/understanding-and-evaluating-template-matching-methods

# candidates for rapid screenshotting: MSS and DXcam, both are designed for high speed captures
# https://python-mss.readthedocs.io/index.html
# https://github.com/ra1nty/DXcam seems to be designed for high rate of screenshotting

# this whole class needs to be refactored into an instance that works well with the greater multi-threaded script
_camera = None
INV_GRID_SIZE = 32


# main is used for visually debugging these methods
def main():
    init_vision()

    while True:
        screenshot = _camera.grab()

        #inv_loc = locate_inventory(screenshot)
        print(f"screenshotshape:{screenshot.shape}")
        pray_orb_loc = locate_prayer_orb(screenshot)

        # get the image of inventory only
        # inv_region = (inv_loc[0] - 20, inv_loc[1] - 20, inv_loc[0] + 147, inv_loc[1] + 237)
        # inv = screenshot[inv_region[1]:inv_region[3], inv_region[0]:inv_region[2]]

        print(f"result={check_flick_failure(screenshot, pray_orb_loc)}")

        # used for debugging find match in inventory
        # match_image4 = _open_image(r"res\Absorb4.png")
        # print(find_matches_in_inventory(match_image4, inv))

        # used for debugging locate inventory
        # for i in range(4):
        #     for j in range(7):
        #         opencv.circle(inv, (int(inv_loc[0] + i * 127 / 3), int(inv_loc[1] + j * 217 / 6)), 15,
        #                       (255, 0, 255))

        # used for debugging locate prayer orb
        # pray_orb_loc = locate_prayer_orb(screenshot)
        # opencv.circle(screenshot, pray_orb_loc, 15, (255, 255, 0))

        # window_name = "CV Output"
        #
        # opencv.namedWindow(window_name)
        # opencv.moveWindow(window_name, 1920, 0)
        #
        # opencv.imshow(window_name, inv)

        if opencv.waitKey(1000) == 27:
            release_vision()
            return


# returns coordinate in x,y format
def locate_inventory(template):
    match_image = _open_image(r"res\InventoryMatcher.png")
    result = opencv.matchTemplate(match_image, template, opencv.TM_SQDIFF)
    val, _, loc, _ = opencv.minMaxLoc(result)
    return loc[0] + 48, loc[1] + 55


# returns coordinate in x,y format
def locate_prayer_orb(template):
    match_image = _open_image(r"res\PrayerOrbMatcher.png")
    result = opencv.matchTemplate(match_image, template, opencv.TM_SQDIFF)
    val, _, loc, _ = opencv.minMaxLoc(result)
    return loc[0] + 35, loc[1] + 64


def find_all_overloads(inventory):
    overloads = find_in_inventory(_open_image(r"res\Overload1.png"), inventory)
    overloads += find_in_inventory(_open_image(r"res\Overload2.png"), inventory)
    overloads += find_in_inventory(_open_image(r"res\Overload3.png"), inventory)
    overloads += find_in_inventory(_open_image(r"res\Overload4.png"), inventory)
    return [ovl[:2] for ovl in overloads]


def find_all_absorbs(inventory):
    absorbs = find_in_inventory(_open_image(r"res\Absorb1.png"), inventory)
    absorbs += find_in_inventory(_open_image(r"res\Absorb2.png"), inventory)
    absorbs += find_in_inventory(_open_image(r"res\Absorb3.png"), inventory)
    absorbs += find_in_inventory(_open_image(r"res\Absorb4.png"), inventory)
    return [ab[:2] for ab in absorbs]


def find_locator_orb(inventory):
    results = find_in_inventory(_open_image(r"res\LocatorOrb.png"), inventory)
    return results[0] if results else None


def check_nmz_exit(screenshot, prayer_orb_loc):
    # broken because coffer is not visible on death
    # rewrite this for full hp?
    top_left = (prayer_orb_loc[0]-12, prayer_orb_loc[1]-53)
    template = screenshot[top_left[1]:top_left[1]+38, top_left[0]:top_left[0]+27]
    image = _open_image(r"res\fullhp.png")
    result = opencv.matchTemplate(image, template, opencv.TM_SQDIFF)
    val, _, _, _ = opencv.minMaxLoc(result)
    return True if val < 1000 else False


def check_flick_failure(screenshot, prayer_orb_loc):
    top_left = (prayer_orb_loc[0]-5, prayer_orb_loc[1]-5)
    template = screenshot[top_left[1]:top_left[1]+10, top_left[0]:top_left[0]+10]
    image = _open_image(r"res\PrayerOrbActive.png")
    result = opencv.matchTemplate(image, template, opencv.TM_SQDIFF)
    val, _, _, _ = opencv.minMaxLoc(result)
    # match values were always 0.0, failures were over 2million
    return True if val < 1000 else False


def check_hp_over_1(screenshot, prayer_orb_loc):
    top_left = (prayer_orb_loc[0]-40, prayer_orb_loc[1]-45)
    template = screenshot[top_left[1]:top_left[1]+30, top_left[0]:top_left[0]+30]
    image = _open_image(r"res\1hp.png")
    result = opencv.matchTemplate(image, template, opencv.TM_SQDIFF)
    val, _, _, _ = opencv.minMaxLoc(result)
    # match values were always 0.0, failures were around 800k
    return False if val < 1000 else True


def find_in_inventory(image, inventory, threshold=50000):
    """
    returns a list of tuples in (x,y,val) format sorted by best match first
    x and y are in inventory grid format (1,2) is the second column, third row
    val is the non-normalized sum of differences of squares of each pixel from match template
    for example, 0-5000 represent exact matches, a 3 dose returns 700,000 when searching for 4
    """
    matches = []
    # the x and y size of each inventory square
    dx = round(inventory.shape[1] / 4)
    dy = round(inventory.shape[0] / 7)

    for i in range(7):
        for j in range(4):
            template = inventory[i * dy:(i + 1) * dy, j * dx:(j + 1) * dx]
            result = opencv.matchTemplate(image, template, opencv.TM_SQDIFF)
            val, _, _, _ = opencv.minMaxLoc(result)
            if val < threshold:
                matches.append((j, i, val))

            # visual debugging tools
            # opencv.namedWindow(f"{j},{i}")
            # opencv.moveWindow(f"{j},{i}", 1920 + j * 64, 0 + i * 64)
            # opencv.imshow(f"{j},{i}", template)
    return sorted(matches, key=lambda x: x[2])


def crop_inventory(inv_loc, screenshot):
    region = (inv_loc[0] - 20, inv_loc[1] - 20, inv_loc[0] + 147, inv_loc[1] + 237)
    return screenshot[region[1]:region[3], region[0]:region[2]]


def get_screenshot(region=None):
    grab = _camera.grab(region)
    while grab is None:
        print("failed to capture screenshot, retrying")
        utils.wait(100)
        grab = _camera.grab(region)
    return grab


def init_vision(gray=False):
    global _camera

    if gray:
        _camera = dxcam.create(output_color="GRAY")
    else:
        _camera = dxcam.create(output_color="BGR")


def release_vision():
    global _camera
    _camera.release()


# the first thread that calls pollKey or waitKey has exclusive control over the window updates
# which means this method will only work to display a static image for debugging
def init_window_thread(window_name, screenshot):
    threading.Thread(target=_window_thread_loop(window_name, screenshot)).start()


def _window_thread_loop(_window_name, screenshot):
    opencv.imshow(_window_name, screenshot)
    while True:
        if opencv.waitKey(1000) == 27:
            opencv.destroyWindow(_window_name)
            return


def _open_image(filename, gray=False):
    if gray:
        return opencv.imread(filename, opencv.IMREAD_GRAYSCALE)
    else:
        # this strips the alpha channel and returns a 3d numpy array in BGR format
        return opencv.imread(filename, opencv.IMREAD_COLOR)


if __name__ == "__main__":
    main()
