from machine import Pin, SPI, I2C
import sdcard
import os
from bme280 import BME280
import time

sda=Pin(20)
scl=Pin(21)
i2c=I2C(0, sda=sda, scl=scl, freq=400000)
i2cScan = i2c.scan()
sensorBME = BME280(i2c=i2c)

spi=SPI(1,baudrate=40000000,sck=Pin(10),mosi=Pin(11),miso=Pin(12))
sd=sdcard.SDCard(spi,Pin(13))

# Create a instance of MicroPython Unix-like Virtual File System (VFS),
vfs=os.VfsFat(sd)
# Mount the SD card
os.mount(sd,'/sd')

with open("/sd/sample.txt", "w") as file:
    for i in range(10):
        tempC, preshPa, humRH = sensorBME.values
        file.write("temp {}, preshPa {}, humRH {} \r\n".format(tempC, preshPa, humRH))
        time.sleep(2)
        print(i)
    
