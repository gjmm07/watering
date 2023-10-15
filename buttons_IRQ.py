from machine import Pin
import micropython


class ButtonsIRQ:
    
    def __init__(self, pin_num):
        self.pin = Pin(pin_num, Pin.IN, Pin.PULL_UP)
        
        self.last_button_status = self.pin.value()
        self._enable_irq()
        self.is_pressed = False
        
    def _enable_irq(self):
        self.pin.irq(self.process_inputs, Pin.IRQ_RISING | Pin.IRQ_FALLING)
            
    def process_inputs(self, name):
        if self.last_button_status == self.pin.value():
            return
        self.last_button_status = self.pin.value()
        if self.pin.value():
            micropython.schedule(self.change_status, 0)
        else:
            micropython.schedule(self.change_status, 1)
        
    def change_status(self, type_):
        if not type_:
            self.is_pressed = True
        
    def pressed(self):
        if self.is_pressed:
            self.is_pressed = False
            return True
        
        
        