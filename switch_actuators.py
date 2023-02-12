# switch actuators
from machine import Pin, ADC
import time

enable = Pin(19, Pin.OUT)
enable.low()
s0 = Pin(16, Pin.OUT)
s1 = Pin(17, Pin.OUT)
s2 = Pin(18, Pin.OUT)

s0_h = Pin(4, Pin.OUT)
s1_h = Pin(5, Pin.OUT)
s2_h = Pin(6, Pin.OUT)
analog = ADC(26)

lst = [(0, 0, 0),
       (0, 1, 1),
       (0, 1, 0),
       (1, 0, 0),
       (0, 0, 1),
       (1, 1, 0),
       (1, 1, 1),
       (1, 0, 1)]

def switch_all():
    while True:
        for i, item in enumerate(lst):
            dict_ = {"0": s0, "1": s1, "2": s2}
            for j, pin in enumerate(item):
                if pin: 
                    dict_[str(j)].high()
                else:
                    dict_[str(j)].low()
            time.sleep(1)
            print(i)
            
            
def switch_single(item=[0, 0, 0]):
    dict_ = {"0": s0, "1": s1, "2": s2}
    for j, pin in enumerate(item):
        if pin: 
            dict_[str(j)].high()
        else:
            dict_[str(j)].low()


def read_sensor():
    while True:
        for i, item in enumerate(lst):
            dict_ = {"0": s0_h, "1": s1_h, "2": s2_h}
            for j, pin in enumerate(item):
                if pin: 
                    dict_[str(j)].high()
                else:
                    dict_[str(j)].low()
            time.sleep(1)
            print(i)
            print(analog.read_u16())


read_sensor()
    




