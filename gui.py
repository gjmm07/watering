from read_buttons import run_selection, print_to_display
from pots import Pots, StateMachine
import utime

SIM = False

class MenuObject:
    def __init__(self, name, slaves, short_name, last=False):
        self.name = name
        self.slaves = slaves
        self.last = last
        self.short_name = short_name

    def return_slaves_name(self):
        if not self.last:
            return [i.name for i in self.slaves]
        return

    def return_slave(self, name):
        for i in self.slaves:
            if i.name == name:
                return i


def menu(master_order):
    while True:
        master = master_order[-1]
        if not master.last:
            if not SIM:
                selection = run_selection(" ".join([x.short_name for x in master_order]), master.return_slaves_name())
            else:
                selection = button_select([x.name for x in master_order], master.return_slaves_name() + ["BACK"])
            if selection != "BACK":
                master_order.append(master.return_slave(selection))
            elif selection == "BACK" and master.name != "MAIN MENU":
                del master_order[-1]
        else:
            if master.slaves is None:
                master_order = yield master_order, "REMOVE ALL"
            else:
                sel = {key: None for key in [x[0] for x in master.slaves.values()]}
                for i in range(len(master.slaves)):
                    if not SIM:
                        selection = run_selection(master.slaves[i][0], master.slaves[i][1])
                    else:
                        selection = button_select(master.slaves[i][0], master.slaves[i][1] + ["BACK"])
                    if selection == "BACK":
                        print_to_display("FAILURE")
                        utime.sleep(1)
                        del master_order[-1]
                        break
                    sel[master.slaves[i][0]] = selection
                else:
                    print_to_display("SUCCESS")
                    utime.sleep(1)
                    master_order = yield master_order, sel
        utime.sleep(0.05)
        menu(master_order)


def main():
    pots = Pots(sim=SIM)
    execute = dict(zip(["ADD POT", "REMOVE SINGLE", "RUN", "REMOVE ALL"], [pots.add_pot, pots.remove_pot, None, pots.reset_to_standard]))
    a = menu([main_menu])
    order, sel = next(a)
    while True:
        print(sel)
        if order[-1].name == "RUN":
            m = StateMachine(pots.pots, sel)
            m.run_machine()
        else:
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
    end_time = ["20", "21", "22"]
    start_time = ["8", "9", "10", "11"]
    run_machine = MenuObject(name="RUN", short_name="RUN", slaves={0: ["Start Time", start_time],
                                                                   1: ["End Time", end_time]}, last=True)

    remove_single = MenuObject(name="REMOVE SINGLE", short_name="RSIN", slaves={0: ["ID", Pots.iden[0]]}, last=True)
    remove_all = MenuObject(name="REMOVE ALL", short_name="RALL", slaves=None, last=True)
    remove_pot = MenuObject(name="REMOVE POT", short_name="RPOT", slaves=(remove_single, remove_all))

    add_pot = MenuObject(name="ADD POT", short_name="APOT",
                         slaves={key: val for key, val in enumerate(zip(["ID", "Humidity", "Pot Size", "Actuator Pin", "Sensor Pin"],
                                                                        [Pots.iden[1], Pots.target_hum, Pots.pot_size, Pots.actuator_pin[1], Pots.sensor_pin[1]]))},
                         last=True)

    main_menu = MenuObject(name="MAIN MENU", short_name="MAMU", slaves=(add_pot, remove_pot, run_machine))
    main()
