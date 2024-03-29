from machine import Pin, ADC, I2C, SPI, UART
import utime
import time
import sdcard
import os
import secrets
from bme280 import BME280 #Import BME280-lib
import Sync_thread
import read_buttons
import _thread

# define hardware pins
sda=Pin(20)
scl=Pin(21)
i2c=I2C(0, sda=sda, scl=scl, freq=400000)
sensorBME = BME280(i2c=i2c)

# wlan = network.WLAN(network.STA_IF)

#spi=SPI(1,baudrate=40000000,sck=Pin(14),mosi=Pin(15),miso=Pin(8))
#sd=sdcard.SDCard(spi,Pin(9))
# Create a instance of MicroPython Unix-like Virtual File System (VFS),
#vfs=os.VfsFat(sd)
# Mount the SD card
#os.mount(sd,'/sd')

uart = UART(1, baudrate=9600, tx=Pin(8), rx=Pin(9))

s0_hsensor = Pin(4, Pin.OUT)
s1_hsensor = Pin(5, Pin.OUT)
s2_hsensor = Pin(6, Pin.OUT)
hsensor = ADC(26)
pump = Pin(13, Pin.OUT)
pump.low()

disable_act = Pin(19, Pin.OUT)
disable_act.high()
s0_act = Pin(16, Pin.OUT)
s1_act = Pin(17, Pin.OUT)
s2_act = Pin(18, Pin.OUT)

hsensor_assignment = {"A": (s0_hsensor.low, s1_hsensor.low, s2_hsensor.low),
                      "B": (s0_hsensor.low, s1_hsensor.high, s2_hsensor.high),
                      "C": (s0_hsensor.low, s1_hsensor.high, s2_hsensor.low),
                      "D": (s0_hsensor.high, s1_hsensor.low, s2_hsensor.low),
                      "E": (s0_hsensor.low, s1_hsensor.low, s2_hsensor.high),
                      "F": (s0_hsensor.high, s1_hsensor.high, s2_hsensor.low),
                      "G": (s0_hsensor.high, s1_hsensor.high, s2_hsensor.high),
                      "H": (s0_hsensor.high, s1_hsensor.low, s2_hsensor.high)}
actuator_assignment = {"A": (s0_act.low, s1_act.low, s2_act.low),
                       "B": (s0_act.low, s1_act.high, s2_act.high),
                       "C": (s0_act.low, s1_act.high, s2_act.low),
                       "D": (s0_act.high, s1_act.low, s2_act.low),
                       "E": (s0_act.low, s1_act.low, s2_act.high),
                       "F": (s0_act.high, s1_act.high, s2_act.low),
                       "G": (s0_act.high, s1_act.high, s2_act.high),
                       "H": (s0_act.high, s1_act.low, s2_act.high)}


class Pots:
    target_hum = ["WET", "MEDIUM", "DRY"]
    pot_size = ["HUGE", "MEDIUM", "SMALL"]
    frequency = ["OFTEN", "MEDIUM", "RARELY"]
    actuator_pin = ([], ["A", "B", "C", "D", "E", "F", "G", "H"])
    sensor_pin = ([], ["A", "B", "C", "D", "E", "F", "G", "H"])
    iden = ([], ["1", "2", "3", "4", "5", "6", "7", "8"])
    
    def __init__(self):
        self.pots = []
    
    def add_pot(self, definition):
        for lst, switch_item in zip([self.iden, self.sensor_pin, self.actuator_pin], [definition.get("ID"), definition.get("Sensor Pin"), definition.get("Actuator Pin")]):
            self.switch_sides(lst, switch_item, True)
        self.pots.append(definition)
        
    def add_reference(self, definition):
        print(definition)

    def remove_pot(self, definition):
        dict_ = [x for x in self.pots if x.get("ID") == definition.get("ID")][0]
        for lst, switch_item in zip([self.iden, self.sensor_pin, self.actuator_pin], [dict_.get("ID"), dict_.get("Sensor Pin"), dict_.get("Actuator Pin")]):
            self.switch_sides(lst, switch_item, False)
        self.pots = [x for x in self.pots if x.get("ID") != definition.get("ID")]
    
    def change_order(self, lst, **kwargs):
        try:
            start_item = lst[kwargs["index"]]
        except KeyError:
            start_item = kwargs["name"]
        if start_item in lst:
            idx = self.actuator_pin[1].index(start_item)
            for i in range(idx):
                zz = lst.pop(0)
                lst.append(zz)
    
    def switch_sides(self, lst, item, forward):
        x, y = (0, 1) if forward else (1, 0)
        lst[x].append(item)
        lst[x].sort()
        lst[y].remove(item)
        lst[y].sort()
    
    def reset_to_standard(self, *a):
        for lst in [self.actuator_pin, self.sensor_pin, self.iden]:
            lst[1].extend(lst[0])
            lst[1].sort()
            lst[0].clear()
        self.pots = []
            
    def return_pot_ids(self):
        return [pot.get("ID") for pot in self.pots]
    
    def __len__(self):
        return len(self.pots)
    
    def find_hsensor(self, *args):
        sync = Sync_thread.SyncSearch()
        sync.add_flag("Search", "Display")
        sync["all"] = True
        second_thread = _thread.start_new_thread(read_buttons.waiting, (sync, "CIR"))
        lim = 1000
        old_data = self.read_hsensor_non_connected()
        # todo: maybe timeout?
        while sync["SEARCH"]:
            data = self.read_hsensor_non_connected()
            bound = [abs(x - y) > lim for x, y in zip(old_data, data)]
            old_data = data
            for name, bo in zip(self.sensor_pin[1], bound):
                if bo:
                    sync.set_result(name)
                    print(name)
                    break
            else:
                continue
            self.change_order(self.sensor_pin[1], name=name)
            break
        sync["Display"] = False
        while sync["SEARCH"]:
            utime.sleep(0.5)
    
    def read_hsensor_non_connected(self):
        data = []
        for pin in self.sensor_pin[1]:
            set_mux(hsensor_assignment.get(pin))
            utime.sleep(0.1)
            data.append(hsensor.read_u16())
        return data
    
    def find_valve(self, *args):
        lst = self.sensor_pin[0] + self.sensor_pin[1]
        idx = 0
        valve_pin = None
        while True:
            sel = read_buttons.run_selection("Valve Pins", lst[idx:] + lst[:idx])
            if sel in ["BACK", "TIMED OUT"]:
                self.change_order(self.actuator_pin[1], name=valve_pin)
                break
            valve_pin = sel
            idx = lst.index(sel)
            print(sel, idx)
            set_mux(actuator_assignment.get(sel))
            disable_act.low()
            time.sleep(0.5)
            disable_act.high()
            
    def flush_system(self, *_):
        print("abc")
        pump.high()
        utime.sleep(2)
        disable_act.low()
        for valve in self.actuator_pin[0]:
            print(valve)
            set_mux(actuator_assignment.get(valve))
            utime.sleep(0.5)
        disable_act.high()
        pump.low()


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
                # yield urequests.get(url).json()["weather"][day]["date"]
                for sample in (hour[name]
                           for hour in urequests.get(url).json()["weather"][day]["hourly"]
                           for name in args):
                    # pass every sample singlehanded to preserve memory
                    yield sample
            print("Success")
            break
        except OSError:
            pass
    else:
        print("No data received")
        return None
    

def set_mux(pins):
    for pin in pins:
        pin()
    
    
def write_serial(header=None, iterable=None):
    if header is not None:
        uart.write(header + "\r\n")
    if iterable is not None:
        if isinstance(iterable, dict):
            for key, val in iterable.items():
                uart.write("{key}: {val}, \r\n".format(key=key, val=val))
        elif isinstance(iterable, list):
            for item in iterable:
                uart.write("{}, \r\n".format(item))
    utime.sleep(0.2)
    

def write_init_file(func):
    def wrapper(self):
        print("init file")
        write_serial("init file")
        write_serial("TIME", self.cur_time)
        write_serial("POTS")
        for pot in self.pots_to_run:
            write_serial(iterable=pot)
        pot_ind = [pot["ID"] for pot in self.pots_to_run]
        write_serial("DATA", ["hour", "minute", "Temp", "Pres", "AHum"] + [i for j in zip(["wat"+ind for ind in pot_ind], ["hum"+ind for ind in pot_ind]) for i in j])
        write_serial("end")
        return func(self)
    return wrapper
    

def write_data(func):
    def wrapper(self):
        print("write data")
        write_serial("write data")
        write_serial("TIME", {"day": self.cur_time["day"], "month": self.cur_time["month"], "year": self.cur_time["year"]})
        pot_data = [i for j in zip(self.watered_pots, [data[-1] for data in self.hsensor_data]) for i in j]
        write_serial("DATA", [self.cur_time["hour"], self.cur_time["minute"]] + self.current_weather + pot_data)
        write_serial("end")
        return func(self)
    return wrapper


class StateMachine:
    
    def __init__(self, pots_to_run, times, sync):
        self.start_time, self.end_time = int(times["Start Time"]), int(times["End Time"])
        self.pots_to_run = pots_to_run
        self.hsensor_data = [[] for _ in range(len(pots_to_run))]
        self.watered_pots = None
        self.last_watered = [0 for _ in range(len(pots_to_run))]
        self.current_weahter = []
        self.cur_time = {}
        self.sync = sync
        self.start_time_run = None
        self.update_time()
        
    def update_time(self):
        self.cur_time = {name: val for name, val in zip(["year", "month", "day", "hour", "minute"], time.localtime())}
    
    @write_init_file
    def run_machine(self):
        """
        runs the watering machine
        """
        next_handler = self.read_hsensors()
        while True:
            print("_____")
            utime.sleep(2)
            self.update_time
            next_handler = next_handler()
            if next_handler is None:
                print("done")
                break
        self.sync["Input Act"] = False
        
    def read_hsensors(self):
        """
        reads humiditiy sensors
        """
        self.start_time_run = time.time()
        for i, pot in enumerate(self.pots_to_run):
            set_mux(hsensor_assignment.get(pot.get("Sensor Pin")))
            utime.sleep(0.1)
            if len(self.hsensor_data[0]) > 3:
                for x in self.hsensor_data:
                    x.pop(0)
            samples, amount = [], 3
            for _ in range(amount):
                samples.append(hsensor.read_u16())
                utime.sleep(0.5)
            self.hsensor_data[i].append(s:=sum(samples) / amount)
            # self.hsensor_data[i].append(sample:=hsensor.read_u16())
            print(pot.get("Sensor Pin"))
            print(s)
        return self.read_weather
    
    def read_weather(self):
        """
        reads weather data
        """
        self.current_weather = [sample for sample in (x.split(token)[0] for x, token in zip(sensorBME.values, ["C", "hPa", "%"]))]
        self.sync.write_weather(*self.current_weather, [sample[-1] for sample in self.hsensor_data])
        if not self.start_time < self.cur_time["hour"] < self.end_time or float(self.current_weather[0]) < 10:
            # do nothing at night do nothing at low temperatures
            self.watered_pots = [False for _ in range(len(self.pots_to_run))]
            return self.idle
        return self.switch_actuators

    def switch_actuators(self):
        """
        Depending on the read humidity, valves will be switched
        """
        hum_boundary = {"WET": 45000, "MEDIUM": 20000, "DRY": 5000}
        last_wat_boundary = {"OFTEN": 600, "MEDIUM": 43200, "RARELY": 259200} # makes 3h, 12h, 3 days
        valve_open_time = {"HUGE": 1, "MEDIUM": 0.5, "SMALL": 0.2}
        self.watered_pots = [False for _ in range(len(self.pots_to_run))]
        i = 0
        normalize_time = 0
        for hum, hum_bound, act_pin, last_wat, last_wat_bound, open_time in zip(self.hsensor_data, [hum_boundary[x.get("Humidity")] for x in self.pots_to_run],
                                                                                [x.get("Actuator Pin") for x in self.pots_to_run], self.last_watered,
                                                                                [last_wat_boundary[x.get("Frequency")] for x in self.pots_to_run],
                                                                                [valve_open_time[x.get("Pot Size")] for x in self.pots_to_run]):
            t = time.time()
            if all([pot_hum < hum_bound for pot_hum in hum]) and t - last_wat > last_wat_bound:
                self.watered_pots[i] = True
                # pump.high()
                disable_act.low()
                utime.sleep(1.5) # build up pressure
                print("valve", act_pin)
                set_mux(actuator_assignment[act_pin])
                utime.sleep(open_time) # keep valve open for time
                normalize_time = 20
            elif all([pot_hum > hum_bound for pot_hum in hum]):
                self.last_watered[i] = t
            i += 1
        pump.low()
        utime.sleep(normalize_time)
        disable_act.high()
        return self.idle
    
    @write_data
    def idle(self):
        disable_act.high()
        pump.low()
        run_once = True
        while time.time() - self.start_time_run < 20 or run_once:
            run_once = False
            utime.sleep(0.5)
            if not self.sync["STATE MACHINE"]:
                return None
        return self.read_hsensors
    

def input_activity(sync, pots):
    utime.sleep(1)
    while True:
        read_buttons.sleep_and_wait()
        sel = read_buttons.run_selection("show", func=sync.return_data, rw_control=True, extra_item={"name":"Breakup", "state":False})
        print(sel)
        if sel == "Breakup":
            if read_buttons.run_selection("Breakup", ["Yes", "No"]) == "Yes":
                sync["State Machine"] = False # kill state machine at suitable time
                read_buttons.print_to_display("Waiting")
                break
    while sync["INPUT ACT"]:
        time.sleep(0.5)
        
        

if __name__ == "__main__":
    pots = Pots()
    pots.add_pot({'Pot Size': 'SMALL', 'Humidity': 'WET', "Frequency": "OFTEN", 'Actuator Pin': 'F', 'ID': '1', 'Sensor Pin': 'E'})
    pots.add_pot({'Pot Size': 'SMALL', 'Humidity': 'WET', "Frequency": "OFTEN", 'Actuator Pin': 'C', 'ID': '2', 'Sensor Pin': 'A'})
    pots.add_pot({'Pot Size': 'SMALL', 'Humidity': 'WET', "Frequency": "OFTEN", 'Actuator Pin': 'B', 'ID': '3', 'Sensor Pin': 'F'})
    
    # pots.flush_system()
    sync = Sync_thread.SyncStateMachine(pots.return_pot_ids())
    sync.add_flag("input act", "State Machine")
    sync["all"] = True
    
    m = StateMachine(pots.pots, {"Start Time": "8", "End Time": "22"}, sync)
    second_thread = _thread.start_new_thread(m.run_machine, ())
    input_activity(sync, pots)
    
    
    
    
        
        
        
        
        
        