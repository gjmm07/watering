
class MenuObject:
    def __init__(self, name, slaves, last=False):
        self.name = name
        self.slaves = slaves
        self.last = last

    def return_slaves_name(self):
        if not self.last:
            return [i.name for i in self.slaves]
        return

    def return_slave(self, name):
        for i in self.slaves:
            if i.name == name:
                return i
            
class Pots:
    target_hum = ["WET", "MEDIUM", "DRY"]
    pot_size = ["HUGE", "MEDIUM", "SMALL"]
    actuator_pin = ([], ["A", "B", "C", "D", "E", "F", "G", "H"])
    sensor_pin = ([], ["A", "B", "C", "D", "E", "F", "G", "H"])
    iden = ([], ["1", "2", "3", "4", "5", "6", "7", "8"])
    def __init__(self):
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
        lst[y].remove(item)



end_time = {"20": 20, "21": 21, "22": 22}
start_time = {"8": 8, "9": 9, "10": 10, "11": 11}
run_machine = MenuObject(name="RUN", slaves=dict(**start_time, **end_time), last=True)

remove_pot = MenuObject(name="REMOVE POT", slaves={0: ["ID", Pots.iden[0]]}, last=True)

add_pot = MenuObject(name="ADD POT",
                     slaves={key: val for key, val in enumerate(zip(["ID", "Humidity", "Pot Size", "Actuator Pin", "Sensor Pin"],
                                                                    [Pots.iden[1], Pots.target_hum, Pots.pot_size, Pots.actuator_pin[1], Pots.sensor_pin[1]]))},
                     last=True)

main_menu = MenuObject(name="MAIN MENU", slaves=(add_pot, remove_pot, run_machine))


def menu(master_order):
    while True:
        master = master_order[-1]
        if not master.last:
            selection = button_select([x.name for x in master_order], master.return_slaves_name() + ["BACK"])
            master_order.append(master.return_slave(selection))
        else:
            sel = {key: None for key in [x[0] for x in master.slaves.values()]}
            for i in range(len(master.slaves)):
                selection = button_select(master.slaves[i][0], master.slaves[i][1] + ["BACK"])
                if selection == "BACK":
                    print("FAILURE")
                    del master_order[-1]
                    break
                sel[master.slaves[i][0]] = selection
            else:
                print("success")
                master_order = yield master_order, sel
        menu(master_order)


def main():
    pots = Pots()
    execute = dict(zip(main_menu.return_slaves_name(), [pots.add_pot, pots.remove_pot, None]))
    a = menu([main_menu])
    order, sel = next(a)
    while True:
        execute[order[-1].name](sel)
        order, sel = a.send([main_menu])


def button_select(header, items):
    print(header)
    while True:
        selection = input("Please select from the following {}: ".format(items[:-1] if items[-1] == "BACK" else items))
        print("\n")
        if selection.upper() in str(items) and selection != "":
            return selection.upper()


if __name__ == "__main__":
    main()