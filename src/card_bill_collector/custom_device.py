import re
import logging
import shlex
from typing import NamedTuple, List, Any

from uiautomator2 import Device

from card_bill_collector.exceptions import NoVisibleWindowError


class Bound(NamedTuple):
    left: int
    top: int
    right: int
    bottom: int

    @property
    def area(self) -> int:
        return (self.right - self.left) * (self.bottom - self.top)



class AndroidWindow(NamedTuple):
    name: str
    is_on_screen: bool
    is_visible: bool
    has_surface: bool
    type: str
    frame: Bound

    FINDER = re.compile(r"Window #\d+ Window\{\w+ \w+ (?P<name>\S+)\}:"
                        r"[\s\S]+?ty=(?P<type>\w+)"
                        r"[\s\S]+?mHasSurface=(?P<has_surface>\w+)"
                        r"[\s\S]+?Frames:[\s\S]+?frame=(?P<frame>\[(?P<left>\d+),(?P<top>\d+)\]\[(?P<right>\d+),(?P<bottom>\d+)\])"
                        r"[\s\S]+?isOnScreen=(?P<is_on_screen>\w+)"
                        r"[\s\S]+?isVisible=(?P<is_visible>\w+)")
    DUMPSYS_WINDOW = "dumpsys window windows"

    @classmethod
    def findall(cls, dev: Device) -> List[Any]:
        windows = []
        for match in cls.FINDER.finditer(dev.shell(cls.DUMPSYS_WINDOW).output):
            windows.append(AndroidWindow(
                name=match.group("name"),
                is_on_screen=match.group("is_on_screen") == "true",
                is_visible=match.group("is_visible") == "true",
                has_surface=match.group("has_surface") == "true",
                type=match.group("type"),
                frame=Bound(*map(lambda item: int(match.group(item)), ["left", "top", "right", "bottom"]))
            ))
        return windows


class CustomDevice(Device):

    UNUSED_WINDOW_TYPES = {"WALLPAPER", "NAVIGATION_BAR_PANEL"}

    def __init__(self, barcode):
        super().__init__(barcode)

        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s %(levelname)s [%(funcName)s] [%(name)s] %(message)s'
        )
        self.logger = logging.getLogger(barcode)

    @property
    def current_window(self):
        try:
            windows = sorted([w for w in self.visible_windows() if w.is_on_screen and w.has_surface],
                             key=lambda _w: (-_w.frame.area, _w.frame.top))
            if len(windows) > 1:
                self.logger.debug("More than one window showing on screen: %s", windows)
            return next(iter(windows))
        except StopIteration as e:
            raise NoVisibleWindowError from e

    def visible_windows(self) -> List[AndroidWindow]:
        return [w for w in AndroidWindow.findall(self) if w.is_visible and w.type not in self.UNUSED_WINDOW_TYPES]

    def insert_text(self, text: str):
        resp = self.shell(f"input text {shlex.quote(text)}")
        return resp.exit_code

