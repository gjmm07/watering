from bme280 import BME280 #Import BME280-lib
from machine import Pin, I2C, SPI
import machine  #Important to get Pins and config them
import time #For a little timer
import sdcard
import os

sda=Pin(20)
scl=Pin(21)
i2c=I2C(0, sda=sda, scl=scl, freq=400000)
i2cScan = i2c.scan()
counter = 0
for i in i2cScan:
    print('I2C Address ' + str(counter) + '     : '+hex(i).upper())
    counter+=1
print('---------------------------')

sensorBME = BME280(i2c=i2c)



i = 0
for _ in range(20):
    tempC, preshPa, humRH = sensorBME.values #Receive current values from GY-BME280 as tuple
    tempC = tempC.replace('C','*C')
    print('Temperatur BME: ' + tempC)
    print('Pressure BME: ' + preshPa)
    print('Humidty BME: ' + humRH)
    print('Counter: ' + str(i))
    print('>-----------<')
    i+=1
    time.sleep(2) #Sleep for two seconds
