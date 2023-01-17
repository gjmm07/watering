from machine import Pin, I2C
import time
from Iterator import Iterator
from machine_i2c_lcd import I2cLcd

back_button = Pin(22, Pin.IN, Pin.PULL_UP)
select_button = Pin(7, Pin.IN, Pin.PULL_UP)
clock_button = Pin(9, Pin.IN)
direction_button = Pin(8, Pin.IN)

# Initialisierung I2C
i2c = I2C(0, sda=Pin(20), scl=Pin(21), freq=100000)

# Initialisierung LCD über I2C
lcd = I2cLcd(i2c, 0x27, 2, 16)


def run_selection(items):
    old_back, old_select, old_clock = 1, 1, 1
    selection = items[0]
    lcd.putstr(selection)
    iterator = Iterator(items)
    while True:
        back, select, clock, direction = back_button.value(), select_button.value(), clock_button.value(), direction_button.value()
        if clock and not old_clock: 
            if direction:
                selection = iterator.reversed_next()
            else:
                selection = iterator.next_()
            lcd.clear()
            lcd.putstr(selection)
        if back != old_back and back:
            return "back"
        elif select != old_select and select:
            return selection
        time.sleep(0.005)
        old_back, old_select, old_clock = back, select, clock


if __name__ == "__main__":
    print(run_selection(["A", "B", "C", "D"]))




