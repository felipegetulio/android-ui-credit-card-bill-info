import logging
import shlex
from typing import  List

from uiautomator2 import Device

from card_bill_collector.exceptions import NoVisibleWindowError
from card_bill_collector.types import AndroidWindow


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

