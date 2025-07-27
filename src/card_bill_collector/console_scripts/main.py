import json
import time
from typing import List

from pcardext import mount

from card_bill_collector.types import Bill, Month
from card_bill_collector.utils import get_1password_reference, collect_expenses
from card_bill_collector.custom_device import CustomDevice


SERIAL = "NGCLD50104"
BANK_PACKAGE = "com.nu.production"
PIN_REFERENCE = f"op://Personal/Devices PIN/add more/{SERIAL}"
DEVICE_PIN = get_1password_reference(PIN_REFERENCE)


def config(d: CustomDevice):
    d.settings["operation_delay"] = (1, 1)
    d.settings["operation_delay_methods"].append("keyevent")
    d.settings["wait_timeout"] = 10



def get_expanses_from_month(d: CustomDevice, month: Month) -> List[Bill]:
    d.unlock()
    if d(text="Enter PIN").exists:
        d.insert_text(DEVICE_PIN)
        d.keyevent("ENTER")


    with d.session(BANK_PACKAGE):
        d(text="Use PIN").click()
        d.insert_text(DEVICE_PIN)
        d.keyevent("ENTER")

        d(descriptionMatches="(?s).*Cartão de crédito.*").click()
        d(descriptionMatches="(?s).*Resumo de faturas.*").click()
        d(**month.value).click()
        time.sleep(2)

        expenses = collect_expenses(d)

        with open(f"expenses_{month.name}.json", "w", encoding="utf-8") as file:
            json.dump(expenses, file, cls=Bill.JSONEncoder, indent=4)





if __name__ == "__main__":
    d = CustomDevice(SERIAL)
    config(d)

    for m in Month:
        get_expanses_from_month(d, m)


