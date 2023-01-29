from machine import Pin, ADC, I2C, SPI
import utime
from bme280 import BME280 #Import BME280-lib
import time
import sdcard
import os

# define hardware pins
sda=Pin(20)
scl=Pin(21)
i2c=I2C(0, sda=sda, scl=scl, freq=400000)
sensorBME = BME280(i2c=i2c)

spi=SPI(1,baudrate=40000000,sck=Pin(14),mosi=Pin(15),miso=Pin(8))
sd=sdcard.SDCard(spi,Pin(9))
# Create a instance of MicroPython Unix-like Virtual File System (VFS),
vfs=os.VfsFat(sd)
# Mount the SD card
os.mount(sd,'/sd')

s0_hsensor = Pin(2, Pin.OUT)
s1_hsensor = Pin(4, Pin.OUT)
s2_hsensor = Pin(3, Pin.OUT)
hsensor = ADC(27)
pump = pump = Pin(13, Pin.OUT)
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
actuator_assignment = {"A": (s0_act.low, s1_act.high, s2_act.low),
                       "B": (s0_act.low, s1_act.high, s2_act.low),
                       "C": (s0_act.low, s1_act.high, s2_act.low),
                       "D": (s0_act.high, s1_act.low, s2_act.low),
                       "E": (s0_act.low, s1_act.low, s2_act.high),
                       "F": (s0_act.high, s1_act.low, s2_act.low),
                       "G": (s0_act.high, s1_act.high, s2_act.high),
                       "H": (s0_act.high, s1_act.low, s2_act.high)}

class Pots:
    target_hum = ["WET", "MEDIUM", "DRY"]
    pot_size = ["HUGE", "MEDIUM", "SMALL"]
    actuator_pin = ([], ["A", "B", "C", "D", "E", "F", "G", "H"])
    sensor_pin = ([], ["A", "B", "C", "D", "E", "F", "G", "H"])
    iden = ([], ["1", "2", "3", "4", "5", "6", "7", "8"])
    
    def __init__(self, sim=True):
        sim = sim
        self.pots = []
    
    def add_pot(self, definition):
        for lst, switch_item in zip([self.iden, self.sensor_pin, self.actuator_pin], [definition.get("ID"), definition.get("Sensor Pin"), definition.get("Actuator Pin")]):
            self.switch_sides(lst, switch_item, True)
        self.pots.append(definition)

    def remove_pot(self, definition):
        dict_ = [x for x in self.pots if x.get("ID") == definition.get("ID")][0]
        for lst, switch_item in zip([self.iden, self.sensor_pin, self.actuator_pin], [dict_.get("ID"), dict_.get("Sensor Pin"), dict_.get("Actuator Pin")]):
            self.switch_sides(lst, switch_item, False)
    
    def switch_sides(self, lst, item, forward):
        x, y = (0, 1) if forward else (1, 0)
        lst[x].append(item)
        lst[x].sort()
        lst[y].remove(item)
    
    def reset_to_standard(self, *a):
        for lst in [self.actuator_pin, self.sensor_pin, self.iden]:
            lst[1].extend(lst[0])
            lst[1].sort()
            lst[0].clear()
     

def read_hsensors(pots_to_run, hsensor_data, watered_pots=None):
    """
    Reads the humidity sensors
    """
    for i, pot in enumerate(pots_to_run):
        set_mux(hsensor_assignment.get(pot.get("Sensor Pin")))
        utime.sleep(0.1)
        if len(hsensor_data[0]) > 3:
            for x in hsensor_data:
                x.pop(0)
        hsensor_data[i].append(hsensor.read_u16())
    return hsensor_data, watered_pots, "SWITCH ACTUATORS"


def switch_actuators(pots_to_run, hsensor_data, watered_pots=None):
    """
    Depending on the read humidity, valves will be switched
    """
    boundary = {"WET": 1000, "MEDIUM": 5000, "DRY": 10000}
    watered_pots = [False for _ in range(len(pots_to_run))]
    for i, hum, pot in zip(list(range(len(hsensor_data))), hsensor_data, pots_to_run):
        if all(list(map(lambda x: x < boundary.get(pot.get("Humidity")), hum))):
            # water pot
            watered_pots[i] = True
            disable_act.low()
            pump.high()
            utime.sleep(0.5) #build up the pressure
            set_mux(actuator_assignment.get(pot.get("Actuator Pin")))
            utime.sleep(0.5) 
            disable_act.high()
    pump.low()
    utime.sleep(0.5)
    return hsensor_data, watered_pots, "IDLE"


def idle(pots_to_run, hsensor_data, watered_pots=None):
    pump.low()
    disable_act.high()
    utime.sleep(1)
    return hsensor_data, watered_pots, "SAVE DATA"


def save_data_sd(pots_to_run, hsensor_data, watered_pots=None):
    """
    Reads the wheather data, wheather forecast and saves everything to sd-card
    """
    temp, air_pressure, rel_airhum = read_wheather_data()
    print(watered_pots)
    year, month, day, hour, minute, *_ = time.localtime()
    filename = "data{}_{}_{}.txt".format(day, month, year)
    with open("/sd/"+ filename, "a+") as file:
        file.write(",".join(map(str, [hour, minute, temp, air_pressure, rel_airhum] + watered_pots)))
    return hsensor_data, watered_pots, "READ SENSORS"


def read_wheather_data():
    temp, pres, rel_airhum = sensorBME.values
    return float(temp.split("C")[0]), float(pres.split("hPa")[0]), float(rel_airhum.split("%")[0])
    
def set_mux(pins):
    for pin in pins:
        pin()


class StateMachine:
    handlers = {"READ SENSORS": read_hsensors,
                "SWITCH ACTUATORS": switch_actuators,
                "IDLE": idle,
                "SAVE DATA": save_data_sd}
    
    def __init__(self, pots_to_run, a):
        print(a)
        self.pots = pots_to_run
        self.hsensor_data = [[] for _ in range(len(self.pots))]
        
    def run_machine(self):
        # todo: read pots only during none-running times,
        # save init file which specifies the running pots
        sensor_data, watered_pots, next_handler = self.handlers["READ SENSORS"](self.pots, self.hsensor_data)
        while True:
            utime.sleep(2)
            sensor_data, watered_pots, next_handler = self.handlers[next_handler](self.pots, sensor_data, watered_pots)
        
        
        

if __name__ == "__main__":
    pots = Pots()
    pots.add_pot({'Pot Size': 'HUGE', 'Humidity': 'WET', 'Actuator Pin': 'E', 'ID': '1', 'Sensor Pin': 'F'})
    pots.add_pot({'Pot Size': 'HUGE', 'Humidity': 'WET', 'Actuator Pin': 'G', 'ID': '2', 'Sensor Pin': 'E'})
    pots.add_pot({'Pot Size': 'HUGE', 'Humidity': 'WET', 'Actuator Pin': 'H', 'ID': '3', 'Sensor Pin': 'G'})
    
    m = StateMachine(pots.pots, {"Start Time": "8", "End Time": "20"})
    m.run_machine()
    
    
    
    
        
        
        
        
        
        