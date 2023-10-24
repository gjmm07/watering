from machine import Pin, ADC, I2C, UART
import utime
from bme280 import BME280
from machine_i2c_lcd import I2cLcd


# # wlan = network.WLAN(network.STA_IF)
# #spi=SPI(1,baudrate=40000000,sck=Pin(14),mosi=Pin(15),miso=Pin(8))
# #sd=sdcard.SDCard(spi,Pin(9))
# # Create a instance of MicroPython Unix-like Virtual File System (VFS),
# #vfs=os.VfsFat(sd)
# # Mount the SD card
# #os.mount(sd,'/sd')

# i2c = I2C(0, sda=Pin(20), scl=Pin(21), freq=100000)

# Initialisierung LCD über I2C
# lcd = I2cLcd(i2c, 0x27, 2, 16)

class LCDDisplay:
    i2c = I2C(0, sda=Pin(20), scl=Pin(21), freq=100000)
    lcd = I2cLcd(i2c, 0x27, 2, 16)
    
    def putstr(self, char):
        self.lcd.putstr(char)
    
    def clear(self):
        self.lcd.clear()
        
    def backlight_off(self):
        self.lcd.backlight_off()
        
    def backlight_on(self):
        self.lcd.backlight_on()
    
    off = backlight_off
    on = backlight_on
        


class BluetoothWriter:
    UART = UART(1, baudrate=9600, tx=Pin(8), rx=Pin(9))
    
    def write(self, *data):
        print(data)
        for d in str(data):
            self.UART.write(d)
        self.UART.write("\r\n")
        

class ConditionSensor:
    i2c=I2C(0, sda=Pin(20), scl=Pin(21), freq=400000)
    SENSOR_BME = BME280(i2c=i2c)
    
    def read(self):
        return dict(zip(["Temp", "Pressure", "rel hum"], self.SENSOR_BME.values))



class Valve:
    S0 = Pin(16, Pin.OUT)
    S1 = Pin(17, Pin.OUT)
    S2 = Pin(18, Pin.OUT)
    MP_LOOKUP = {"A": (S0.low, S1.low, S2.low),
                 "B": (S0.low, S1.high, S2.high),
                 "C": (S0.low, S1.high, S2.low),
                 "D": (S0.high, S1.low, S2.low),
                 "E": (S0.low, S1.low, S2.high),
                 "F": (S0.high, S1.high, S2.low),
                 "G": (S0.high, S1.high, S2.high),
                 "H": (S0.high, S1.low, S2.high)}
    DISABLE = Pin(19, Pin.OUT)
    
    def disable(self):
        self.DISABLE.high()
        
    def _enable(self):
        self.DISABLE.low()
        
    def open_(self, pin):
        self._enable()
        for s in self.MP_LOOKUP[pin]:
            s()
    close = disable
            

class HumSensor:
    
    S0 = Pin(4, Pin.OUT)
    S1 = Pin(5, Pin.OUT)
    S2 = Pin(6, Pin.OUT)
    SENSOR = ADC(26)
    # Multiplexer Lookup because not __getattribute__ in micropython
    MP_LOOKUP = {"A": (S0.low, S1.low, S2.low),
                 "B": (S0.low, S1.high, S2.high),
                 "C": (S0.low, S1.high, S2.low),
                 "D": (S0.high, S1.low, S2.low),
                 "E": (S0.low, S1.low, S2.high),
                 "F": (S0.high, S1.high, S2.low),
                 "G": (S0.high, S1.high, S2.high),
                 "H": (S0.high, S1.low, S2.high)}
    
    def read(self, pin: str):
        for s in self.MP_LOOKUP[pin]:
            s()
        if pin == "E":
            # currently another sensor type is connected at Sensor E
            return 1 - self.SENSOR.read_u16() / 65535
        else:
            return self.SENSOR.read_u16() / 65535
    

    
class Pump:
    
    PIN = Pin(13, Pin.OUT)
    
    def on(self):
        self.PIN.high()
        
    def off(self):
        self.PIN.low()
        
    high = on
    low = off
        

if __name__ == "__main__":
    LCDDisplay().backlight_off()
    Pump().off()
    for let in "ABCDEFGH":
        print(HumSensor().read(let))
    print(ConditionSensor().read())
        
        
        
        
        
        
        
        
        
        
        
            
