import network
import secrets
import time
import urequests

wlan = network.WLAN(network.STA_IF)
wlan.active(True)

wlan.connect(secrets.SSID, secrets.PASSWORD)

print(wlan.isconnected())

astronauts = urequests.get("https://wttr.in/Cologne?format=j1").json()
print(astronauts)
