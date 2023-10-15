import Hardware
import utime
from pots import Pots
from Menu import Menu


def find_valve(act_pin_instance: Menu, pots_instance: Pots, act_pin: str, *args, **kwargs):
    print("find valve")
    Hardware.Valve().open_(act_pin)
    utime.sleep(0.5)
    Hardware.Valve().disable()
    try:
        act_pin_instance.index = pots_instance.act_pin[1].index(act_pin)
    except ValueError:
        pass
    

def find_sensor(sen_pin_instance: Menu, pots_instance: Pots, sen_pin: str, *args, **kwargs):
    print("find sensor")
    try:
        sen_pin_instance.index = pots_instance.sen_pin[1].index(sen_pin)
    except ValueError:
        pass
    return Hardware.HumSensor().read(sen_pin)


def flush_sys(current_act_p, *args, **kwargs):
    Hardware.Pump().high()
    utime.sleep(1)
    for let in current_act_p:
        Hardware.Valve().open_(let)
        utime.sleep(0.2)
    Hardware.Pump().off()

