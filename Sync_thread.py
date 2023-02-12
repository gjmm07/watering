class Sync:
    def __init__(self, flag_amount):
        self.flag = [False for _ in range(flag_amount)]
        
    def set_flag(self, index, state):
        self.flag[index] = state

# Inherit!! from top class

class SyncStateMachine:
    def __init__(self, ids=None):
        self.temp = 0
        self.air_hum = 0
        self.pressure = 0
        self.pot_hum = []
        self.flag = False
        self.flag2 = False
        self.pot_ids = ids
    
    def write_weather(self, temp, pressure, air_hum, pot_hum):
        self.temp = temp
        self.pressure = pressure
        self.air_hum = air_hum
        self.pot_hum = pot_hum
    
    def return_data(self):
        return [item.format(val=val) for item, val in zip(["Tp {val} C", "AiHu {val} %", "Prs {val} hPa"] +
                                                          [s + " {val}" for s in ["pot{iden}".format(iden=iden) for iden in self.pot_ids]],
                                                          [self.temp, self.air_hum, self.pressure] + self.pot_hum)]

    
    def set_flag(self, state):
        self.flag = state
        
    def set_flag2(self, state):
        self.flag2 = state



class SyncSearch:

    
    
    
    
    
    
    
    
    
    
        