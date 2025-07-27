from .custom_device import CustomDevice

SERIAL = "NGCLD50104"
BANK_PACKAGE = "com.nu.production"


if __name__ == "__main__":
    d = CustomDevice(SERIAL)

    with d.session(BANK_PACKAGE):
        password = "4528"
        d(text="Use PIN").click()
        d.insert_text(password)
        d.keyevent("ENTER")
        time.sleep(4)
