from machine import Pin, SPI, I2C
import sdcard
import os
import time

spi=SPI(1,baudrate=40000000,sck=Pin(14),mosi=Pin(15),miso=Pin(8))
sd=sdcard.SDCard(spi,Pin(9))

# Create a instance of MicroPython Unix-like Virtual File System (VFS),
vfs=os.VfsFat(sd)
# Mount the SD card
os.mount(sd,'/sd')

with open("/sd/sample.txt", "w") as file:
    for i in range(10):
        file.write("temp {}, preshPa {}, humRH {} \r\n".format("A", "B", "C"))
        time.sleep(2)
        print(i)
    
