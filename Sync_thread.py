class Sync:
    def __init__(self, ids):
        self.temp = 0
        self.air_hum = 0
        self.pressure = 0
        self.pot_hum = []
        self.run_state_machine = False
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

    
    def set_run_sm(self, state):
        self.run_state_machine = state