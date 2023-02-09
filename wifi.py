import urequests, network, secrets, utime

wlan = network.WLAN(network.STA_IF)

def activate_wifi(func):
    def wrapper(url, *args):
        for _ in range(5):
            if wlan.isconnected():
                return func(url, *args)
            else:
                wlan.active(True)
                wlan.connect(secrets.SSID, secrets.PASSWORD)
                utime.sleep(0.5)
    return wrapper
            
@activate_wifi
def acquire_data(url, *args):
    for _ in range(10):
        try:
            for day in range(3):
                # light programming as memory is limited
                yield urequests.get(url).json()["weather"][day]["date"]
                for sample in (hour[name]
                           for hour in urequests.get(url).json()["weather"][day]["hourly"]
                           for name in args):
                    # pass every sample singlehanded to preserve memory
                    yield sample
            break
        except OSError:
            pass
    else:
        print("No data received")
        return None
    
    

gen = acquire_data("https://wttr.in/Cologne?format=j1", "time", "humidity", "precipMM", "pressure",
                   "tempC", "winddirDegree", "windspeedKmph")

for g in gen:
    if type(g) == str:
        print(g)
    else:
        for zz in g:
            print(zz)
