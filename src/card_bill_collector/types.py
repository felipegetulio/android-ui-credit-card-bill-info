import datetime
import json
import re
from enum import Enum
from typing import NamedTuple, List, Any

from uiautomator2 import Device
from moneyed import Money


class Month(Enum):
    MAY = dict(descriptionMatches="(?s).*MAI.*")
    JUN = dict(descriptionMatches="(?s).*JUN.*")
    JUL = dict(descriptionMatches="(?s).*JUL.*")
    AUG = dict(descriptionMatches="(?s).*AGO.*")


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


class Bill(NamedTuple):
    date: datetime.datetime
    description: str
    value: Money

    class JSONEncoder(json.JSONEncoder):
        def default(self, o):
            if isinstance(o, datetime.datetime):
                return o.isoformat()

            if isinstance(o, Money):
                return dict(amount=float(o.amount), currency=str(o.currency))

            if isinstance(o, Bill):
                return o._asdict()

            return super().default(o)

