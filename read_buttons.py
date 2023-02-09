from machine import Pin, I2C
import time, utime
from Iterator import Iterator
from machine_i2c_lcd import I2cLcd

back_button = Pin(22, Pin.IN, Pin.PULL_UP)
select_button = Pin(10, Pin.IN, Pin.PULL_UP)
clock_button = Pin(11, Pin.IN)
direction_button = Pin(12, Pin.IN)

# Initialisierung I2C
i2c = I2C(0, sda=Pin(20), scl=Pin(21), freq=100000)

# Initialisierung LCD über I2C
lcd = I2cLcd(i2c, 0x27, 2, 16)

def print_to_display(text):
    lcd.clear()
    lcd.putstr(text)


def run_selection(header, iter_items, timeout=20):
    if len(iter_items) == 0:
        return
    if timeout is None:
        criteria = lambda *a: True
    else:
        criteria = lambda st, to: (time.time() - st) < to
    selection = iter_items[0]
    lcd.clear()
    lcd.putstr(header + "\n" + selection)
    iterator = Iterator(iter_items)
    old_back, old_select, old_clock = 1, 1, 1
    start_time = time.time()
    while criteria(start_time, timeout):
        back, select, clock, direction = back_button.value(), select_button.value(), clock_button.value(), direction_button.value()
        if clock and not old_clock: 
            if direction:
                selection = iterator.reversed_next()
            else:
                selection = iterator.next_()
            lcd.clear()
            lcd.putstr(header + "\n" + selection)
            start_time = time.time()
        if back != old_back and back:
            return "BACK"
        elif select != old_select and select:
            return selection
        time.sleep(0.005)
        old_back, old_select, old_clock = back, select, clock
    return "TIMED OUT"


def sleep_and_wait():
    lcd.clear()
    lcd.backlight_off()
    old_back, old_select = 1, 1
    while True:
        back, select = back_button.value(), select_button.value()
        utime.sleep(0.05)
        if back != old_back and back:
            break
        elif select != old_select and select:
            break
        old_back, old_select = back, select
    lcd.backlight_on()
        


if __name__ == "__main__":
    print(run_selection("abcd", ["A", "B", "C", "D"]))




