from machine import Pin, ADC
import utime

# define hardware pins
s0_hsensor = Pin(2, Pin.OUT)
s1_hsensor = Pin(4, Pin.OUT)
s2_hsensor = Pin(3, Pin.OUT)
hsensor = ADC(27)

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
     

def read_sensors(pots_to_run, hsensor_data):
    """ Reads the humidity sensors
    # todo: don't let lists grow infit
    """
    for i, pot in enumerate(pots_to_run):
        set_mux(hsensor_assignment.get(pot.get("Sensor Pin")))
        utime.sleep(0.1)
        hsensor_data[i].append(hsensor.read_u16())
    return hsensor_data, "SWITCH ACTUATORS"

def switch_actuators(pots_to_run, hsensor_data):
    """ Depending on the read humidity, valves will be switched"""
    print("switch actuators")
    utime.sleep(0.5)
    return hsensor_data, "READ SENSORS"


def set_mux(pins):
    for pin in pins:
        pin()


class StateMachine:
    handlers = {"READ SENSORS": read_sensors,
                "SWITCH ACTUATORS": switch_actuators}
    
    def __init__(self, pots_to_run, a):
        print(a)
        self.pots = pots_to_run
        self.hsensor_data = [[] for _ in range(len(self.pots))]
        
    def run_machine(self):
        sensor_data, next_handler = self.handlers["READ SENSORS"](self.pots, self.hsensor_data)
        while True:
            print(sensor_data)
            utime.sleep(2)
            sensor_data, next_handler = self.handlers[next_handler](self.pots, sensor_data)
        
        
        

if __name__ == "__main__":
    pots = Pots()
    pots.add_pot({'Pot Size': 'HUGE', 'Humidity': 'WET', 'Actuator Pin': 'E', 'ID': '1', 'Sensor Pin': 'F'})
    pots.add_pot({'Pot Size': 'HUGE', 'Humidity': 'WET', 'Actuator Pin': 'G', 'ID': '2', 'Sensor Pin': 'E'})
    pots.add_pot({'Pot Size': 'HUGE', 'Humidity': 'WET', 'Actuator Pin': 'H', 'ID': '3', 'Sensor Pin': 'G'})
    
    m = StateMachine(pots.pots, {"Start Time": "8", "End Time": "20"})
    m.run_machine()
    
    
    
    
        
        
        
        
        
        