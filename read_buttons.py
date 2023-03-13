from machine import Pin, I2C
import time, utime
from Iterator import Iterator
from machine_i2c_lcd import I2cLcd
import random

back_button = Pin(22, Pin.IN, Pin.PULL_UP)
select_button = Pin(10, Pin.IN, Pin.PULL_UP)
clock_button = Pin(11, Pin.IN)
direction_button = Pin(12, Pin.IN)

# Initialisierung I2C
i2c = I2C(0, sda=Pin(20), scl=Pin(21), freq=100000)

# Initialisierung LCD über I2C
lcd = I2cLcd(i2c, 0x27, 2, 16)

def iterator(iterable, rw_control, *args):
    num = 0
    frequent_check = False
    for arg in args:
        if arg is not None:
            extra_name = arg["name"]
            if isinstance(iterable, list):
                lst = iterable + [arg["name"]]
            else:
                frequent_check = True
            rw_control = rw_control + [arg["state"]]
        else:
            if isinstance(iterable, list):
                lst = iterable
            else:
                frequent_check = True
    while True:
        if frequent_check: 
            lst = iterable() + [arg["name"]]
        x = yield lst[num], rw_control[num]
        num += int(x)
        if num >= len(lst) or num <= -len(lst):
            num = 0


def run_selection(header, iter_items=None, func=None, rw_control=False, timeout=20, **kwargs):
    lcd.clear()
    assert iter_items != func
    if iter_items is None:
        gen = iterator(func, [rw_control] * len(func()), kwargs.get("extra_item"))
    elif func is None:
        gen = iterator(iter_items, [rw_control] * len(iter_items), kwargs.get("extra_items"))
    else:
        raise TypeError("Either specifiy func or iter_items")
    
    if timeout is None:
        criteria = lambda *a: True
    else:
        criteria = lambda st, to: (time.time() - st) < to
    
    selection, rw = next(gen)
    lcd.clear()
    lcd.putstr(header + "\n" + selection)
    old_back, old_select, old_clock = 1, 1, 1
    start_time = time.time()
    update_time = start_time
    while criteria(start_time, timeout):
        back, select, clock, direction = back_button.value(), select_button.value(), clock_button.value(), direction_button.value()
        if clock and not old_clock: 
            if direction:
                selection, rw = gen.send(-1)
            else:
                selection, rw = gen.send(1)
            lcd.clear()
            lcd.putstr(header + "\n" + selection)
            start_time = time.time()
        if not rw:
            if back != old_back and back:
                return "BACK"
            elif select != old_select and select:
                return selection
        else:
            if time.time() - update_time > 1:
                selection, rw = gen.send(0)
                lcd.clear()
                lcd.putstr(header + "\n" + selection)
                update_time = time.time()
        old_back, old_select, old_clock = back, select, clock
    return "TIMED OUT"
        


def waiting(sync, text="CALC"):
    lcd.clear()
    lcd.putstr(text)
    counter, max_counter = 1, 6
    while sync["DISPLAY"]:
        lcd.putchar(".")
        counter += 1
        if counter >= max_counter:
            counter = 1
            lcd.clear()
            lcd.putstr(text)
        start_time = time.time()
        while time.time() - start_time < 0.5:
            if not back_button.value():
                break
        else:
            continue
        print("thread killed")
        break
    lcd.clear()
    lcd.putstr(str(sync.result))
    utime.sleep(0.5)
    sync["Search"] = False
        
        
def print_to_display(text):
    lcd.clear()
    lcd.putstr(text)


def read_select():
    while True:
        if not select_button.value():
            print("pressed")


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
        

def func():
    return [str(random.random()) for _ in range(5)]

if __name__ == "__main__":
    # read_select()
    print(run_selection("show", func=func, rw_control=True, extra_item={"name":"Breakup", "state":False}))




