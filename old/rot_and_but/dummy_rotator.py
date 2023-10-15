import sys
import time
from rotaryIRQ import RotaryIRQ
from buttons_IRQ import ButtonsIRQ

if __name__ == "__main__":
    pin_dt = 12
    pin_clk = 11
    pin_sw = 10
    pin_back = 22
    

    r = RotaryIRQ(pin_num_clk=11,
                  pin_num_dt=12,
                  min_val=0,
                  max_val=5,
                  reverse=False,
                  range_mode=RotaryIRQ.RANGE_WRAP)
    
    back = ButtonsIRQ("back", 22)
    select = ButtonsIRQ("select", 10)

    val_old = r.value()
    while True:
            
        val_new = r.value()
        if val_old != val_new:
            val_old = val_new
            print('result =', val_new)

    time.sleep_ms(50)