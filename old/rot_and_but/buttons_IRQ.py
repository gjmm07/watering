from machine import Pin
import micropython


class ButtonsIRQ:
    
    def __init__(self, pin_name, pin_num):
        self.pin = Pin(pin_num, Pin.IN, Pin.PULL_UP)
        
        self.last_button_status = self.pin.value()
        
        self._enable_irq()
        
    def _enable_irq(self):
        self.pin.irq(self.process_inputs, Pin.IRQ_RISING | Pin.IRQ_FALLING)
            
    def process_inputs(self, name):
        if self.last_button_status == self.pin.value():
            return
        self.last_button_status = self.pin.value()
        if self.pin.value():
            micropython.schedule(self.call_handlers, 0)
        else:
            micropython.schedule(self.call_handlers, 1)
        
    def call_handlers(self, type_):
        print(type_)
        
        
        