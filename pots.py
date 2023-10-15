import Hardware


def _switch_sides(lst, item, direction):
        x, y = (0, 1) if direction else (1, 0)
        lst[x].append(item)
        lst[x].sort()
        lst[y].remove(item)
        lst[y].sort()


class Pots:
    
    HUMIDITY = ["WET", "MEDIUM", "DRY"]
    FREQUENCY = ["OFTEN", "MEDIUM", "RARLY"]
    SIZE = ["HUGE", "BIG", "MEDIUM", "SMALL"]
    
    
    def __init__(self):
        self.act_pin = ([], list("ABCDEFGH"))
        self.sen_pin = ([], list("ABCDEFGH"))
        self.indices = ([], [1, 2, 3, 4, 5, 6, 7])
        
        self.pots = {}
        
    def add_pot(self, ind, hum, freq, size, sen_pin, act_pin):
        print(ind, hum, freq, size, sen_pin, act_pin)
        for lst, item in zip([self.indices, self.act_pin, self.sen_pin], [ind, act_pin, sen_pin]): 
            _switch_sides(lst, item, True)
        self.pots[ind] = {"act_pin": act_pin,
                          "sen_pin": sen_pin,
                          "hum": hum,
                          "freq": freq,
                          "size": size}
        print(self.pots)
        
    def remove_pot(self, ind):
        r_pot = self.pots.pop(ind)
        for lst, item in zip([self.indices, self.act_pin, self.sen_pin], [ind, r_pot["act_pin"], r_pot["sen_pin"]]): 
            _switch_sides(lst, item, False)
        
    def remove_all(self, *args, **kwargs):
        print("rremove")
        for actual, possible in [self.act_pin, self.sen_pin, self.indices]:
            possible += actual
            actual.clear()
            possible.sort()
        self.pots = {}
        
    def display_setup(self):
        print(self.pots)
        print(self.act_pin)
        print(self.sen_pin)
        print(self.indices)
    

