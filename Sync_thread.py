class Sync:
    def __init__(self):
        self.flag = {}

    def add_flag(self, *name):
        for n_name in name:
            self.flag[n_name.upper()] = False

    def __setitem__(self, key, value):
        key = key.upper()
        if key in self.flag.keys():
            self.flag[key] = value
        elif key == "ALL":
            for dict_key in self.flag.keys():
                self.flag[dict_key] = value
        else:
            raise ValueError("Value Not Allowed")


class SyncStateMachine(Sync):
    def __init__(self, ids=None):
        super().__init__()
        self.temp = 0
        self.air_hum = 0
        self.pressure = 0
        self.pot_hum = []
        self.pot_ids = ids

    def write_weather(self, temp, pressure, air_hum, pot_hum):
        self.temp = temp
        self.pressure = pressure
        self.air_hum = air_hum
        self.pot_hum = pot_hum

    def return_data(self):
        return [item.format(val=val) for item, val in zip(["Tp {val} C", "AiHu {val} %", "Prs {val} hPa"] +
                                                          [s + " {val}" for s in
                                                           ["pot{iden}".format(iden=iden) for iden in self.pot_ids]],
                                                          [self.temp, self.air_hum, self.pressure] + self.pot_hum)]
    
class SyncSearch(Sync):
    def __init__(self):
        super().__init__()
        self.result = None
    
    def set_result(self, input_):
        self.result = input_

if __name__ == "__main__":
    flag = SyncStateMachine(["1", "2"])
    flag.add_flag("Flag 1")
    flag.add_flag("Flag 2")
    flag["all"] = True
