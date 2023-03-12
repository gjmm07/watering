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

def iterator(func, rw_control):
    lst = func() + ["Breakup"]
    print(lst)
    num = 0
    while True:
        x = yield lst[num], False
        num += int(x)
        if num >= len(lst) or num <= -len(lst):
            num = 0
            

def run_selection(header, iter_items, rw_control=False, timeout=20, **kwargs):
    lcd.clear()
    if isinstance(iter_items, list): 
        if len(iter_items) == 0:
            return
    else:
        func = iter_items
    if not rw_control:
        # True = read only, False = write
        # make all False 
        rw_control = [False for _ in iter_items]
    if timeout is None:
        criteria = lambda *a: True
    else:
        criteria = lambda st, to: (time.time() - st) < to
    gen = iterator(func, rw_control)
    selection = next(gen)[0]
    lcd.clear()
    lcd.putstr(header + "\n" + selection)
    
    old_back, old_select, old_clock = 1, 1, 1
    start_time = time.time()
    update_time = start_time
    rw = False
    while criteria(start_time, timeout):
        back, select, clock, direction = back_button.value(), select_button.value(), clock_button.value(), direction_button.value()
        if clock and not old_clock: 
            if direction:
                selection, rw = gen.send(1)
            else:
                selection, rw = gen.send(-1)
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
                # iterator.update_collection(update_iteritems(func, rw_control, kwargs["extra_item"])[0])
                # selection, rw = iterator.current
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


def update_iteritems(func, control, kwargs):
    iter_items = func()
    rw_control = [control for _ in range(len(iter_items))]
    rw_control.insert(kwargs["position"] if kwargs["position"] != "end" else len(rw_control), kwargs["state"])
    iter_items.insert(kwargs["position"] if kwargs["position"] != "end" else len(rw_control), kwargs["name"])
    return iter_items, rw_control
    

def run_selection2(header, iter_items, rw_control=False, timeout=20, **kwargs):
    lcd.clear()
    if isinstance(iter_items, list): 
        if len(iter_items) == 0:
            return
    else:
        func = iter_items
        iter_items, rw_control = update_iteritems(func, rw_control, kwargs["extra_item"])
    if not rw_control:
        # True = read only, False = write
        # make all False 
        rw_control = [False for _ in iter_items]
    iterator = Iterator(iter_items, rw_control)
    assert len(iter_items) == len(rw_control)
    if timeout is None:
        criteria = lambda *a: True
    else:
        criteria = lambda st, to: (time.time() - st) < to
    selection = iter_items[0]
    lcd.clear()
    lcd.putstr(header + "\n" + selection)
    
    old_back, old_select, old_clock = 1, 1, 1
    start_time = time.time()
    update_time = start_time
    rw = rw_control[0]
    while criteria(start_time, timeout):
        back, select, clock, direction = back_button.value(), select_button.value(), clock_button.value(), direction_button.value()
        if clock and not old_clock: 
            if direction:
                selection, rw = iterator.reversed_next()
            else:
                selection, rw = iterator.next_()
            lcd.clear()
            lcd.putstr(header + "\n" + iterator.current[0])
            start_time = time.time()
        if not rw:
            if back != old_back and back:
                return "BACK"
            elif select != old_select and select:
                return selection
        else:
            if time.time() - update_time > 1:
                iterator.update_collection(update_iteritems(func, rw_control, kwargs["extra_item"])[0])
                selection, rw = iterator.current
                lcd.clear()
                lcd.putstr(header + "\n" + selection)
                update_time = time.time()
        old_back, old_select, old_clock = back, select, clock
    return "TIMED OUT"


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
        


if __name__ == "__main__":
    # read_select()
    print(run_selection("abcd", ["A", "B", "C", "D"]))




