import datetime
import json
import re
import subprocess
import time
from typing import Dict, List

import uiautomator2.exceptions
from moneyed import Money, BRL
from uiautomator2 import Device
from ordered_set import OrderedSet

from .types import Bill




def get_item_from_1password(item: str) -> Dict:
    output = subprocess.check_output(f'op item get {repr(item)} --format json', shell=True, text=True)
    return json.loads(output)


def get_1password_reference(reference: str):
    output = subprocess.check_output(f'op read {repr(reference)}', shell=True, text=True)
    return output.rstrip()


def _capture_from_screen(d, kwargs):
    descriptions = []

    for ui_obj in d(**kwargs):
        try:
            descriptions.append(ui_obj.info["contentDescription"])
        except uiautomator2.exceptions.UiObjectNotFoundError:
            pass

    return descriptions


def collect_expenses(d: Device) -> List[Bill]:
    kw_find_expense = dict(descriptionMatches=r"(?ims)^\d+ [A-Z]+.*\d+,\d+.*$")
    bills_finder = re.compile(r"(?P<date>\d+ \w{3}).*\n(?P<description>.*)\nR\$ (?P<value>.*)")

    all_bills = OrderedSet()
    last_screen = None
    screen = d.dump_hierarchy()

    while screen != last_screen:
        all_bills.update(_capture_from_screen(d, kw_find_expense))
        d.swipe_ext("up", scale=.4)
        time.sleep(.5)

        last_screen = screen
        screen = d.dump_hierarchy()

    obj_bills = []

    for str_bill in all_bills:
        m = bills_finder.search(str_bill)
        if m:
            obj_bills.append(Bill(
                date=m.group("date"),
                description=m.group("description"),
                value=Money(m.group("value").replace(".", "").replace(",", "."), BRL)
            ))

    return obj_bills
