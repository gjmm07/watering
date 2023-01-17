# Bibliotheken laden
from time import sleep_ms
from machine import I2C, Pin
from machine_i2c_lcd import I2cLcd

# Initialisierung I2C
i2c = I2C(0, sda=Pin(20), scl=Pin(21), freq=100000)

# Initialisierung LCD über I2C
lcd = I2cLcd(i2c, 0x27, 2, 16)

# Text in Zeilen
zeile_oben  = 'Hello World';
zeile_unten = 'Hurra ich lebe'

# Display-Zeilen ausgeben
lcd.putstr(zeile_oben + "\n" + zeile_unten)
sleep_ms(3000)

# Display-Inhalt löschen
lcd.clear()
sleep_ms(1000)

# Position im Display
for zeile in range (0,2):
    for spalte in range (0,16):
        lcd.move_to(spalte, zeile)
        lcd.putstr('.')
        sleep_ms(300)

print("Hintergrundlicht aus")
lcd.backlight_off()
sleep_ms(3000)

print("Display aus")
lcd.display_off()
sleep_ms(3000)
