from machine_i2c_lcd import I2cLcd
from machine import Pin, I2C
import utime
from Hardware import LCDDisplay


# Initialisierung I2C
i2c = I2C(0, sda=Pin(20), scl=Pin(21), freq=100000)

# Initialisierung LCD über I2C
lcd = I2cLcd(i2c, 0x27, 2, 16)


class Menu:
    
    def __init__(self, name: str, short_name: str, slaves: list, *func_args, key: str = None):
        self.name = name
        self.short_name = short_name
        self.slaves = slaves
        self.key = key
        self.index = 0
        self.func_args = func_args
        
        # self.prefix = ["" for _ in self.slaves]
        # self.suffix = ["" for _ in self.slaves]
        
    def initialize(self):
        if isinstance(self.slaves[self.index], Menu):
            self.update_display(self.slaves[self.index].name)
        else:
            self.update_display(self.slaves[self.index])
        
    def select(self):
        return self.key, self.slaves[self.index]
        
    def backwards(self):
        print("backwards")
        
    def increment(self, dir_):
        self.index += dir_
        if self.index >= len(self.slaves):
            self.index = 0
        elif self.index < 0:
            self.index = len(self.slaves) - 1
        self.initialize()
    
    def update_display(self, display:str, prefix: str = "", suffix: str = ""):
        LCDDisplay().clear()
        try:
            # not probely working jet
            LCDDisplay().putstr(str(self.prefix[self.index]) + str(display) + str(self.suffix[self.index]))
        except IndexError:
            LCDDisplay().putstr(str(display))
        except AttributeError:
            LCDDisplay().putstr(str(display))
        
        

class CollectorMenu(Menu):
    
    def __init__(self,
                 name: str,
                 short_name: str,
                 slaves: list,
                 function,
                 *func_args,
                 key: str = None):
        
        super().__init__(name, short_name, slaves, *func_args, key=key)
        
        
        self.kwargs = [key] if key is not None else []
        if slaves is not None:
            for slave in slaves:
                try:
                    self.kwargs.append(slave.key)
                except AttributeError:
                    pass
        # self.func_args = func_args
        self.kwargs = dict.fromkeys(self.kwargs)
        
        self.ready_to_exe = False
        self.function = function
        self.handler = None
        
    def collect_data(self, key, value):
        self.kwargs[key] = value
        self.ready_to_exe = all([x is not None for x in self.kwargs.values()])
    
    
    def collect_data2(self, key, value):
        # self.kwargs[key] = value
        # self.suffix[[slave.key for slave in self.slaves].index(key)] = value
        if all([x is not None for x in self.kwargs.values()]):
            print(self.kwargs)
            if self.handler is not None:
                self.handler(**self.kwargs)
            self.reset()
            return True
        return False
        
    def reset(self):
        self.kwargs = {slave.key: None for slave in self.slaves}
        self.suffix = ["" for _ in self.slaves]
        
    def add_handler(self, handler):
        self.handler = handler
        
    def show_short(self, value, time):
        LCDDisplay().clear()
        LCDDisplay().putstr(str(value))
        utime.sleep(time)
    

        
        
        
    
    

