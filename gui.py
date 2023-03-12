from read_buttons import run_selection, print_to_display, sleep_and_wait
from pots import Pots, StateMachine, input_activity
import utime
import time, _thread
import Sync_thread

class MenuObject:
    def __init__(self, name, slaves, short_name, last=False):
        self.name = name
        self.slaves = slaves
        self.hidden_slaves = {}
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
    
    def hide_slaves(self, *names):
        self.hide_none()
        mask = [x not in names for x in self.return_slaves_name()]
        hidden, non_hidden = {}, []
        for i, n_mask in enumerate(mask):
            if n_mask:
                non_hidden.append(self.slaves[i])
            else:
                hidden[i] = self.slaves[i]
        self.slaves = non_hidden
        self.hidden_slaves = hidden
        
    def hide_none(self):
        for index, slave in self.hidden_slaves.items():
            self.slaves.insert(index, slave)
            


def hide_non_executable(func):
    def wrapper(master_order):
        if (obj:=master_order[-1]).name == "MAIN MENU":
            print(len(pots))
            if len(pots) == 0:
                obj.hide_slaves("REMOVE POT", "RUN")
            else:
                obj.hide_none()
        elif obj.name == "FIND HARDWARE":
            if not len(pots):
                obj.hide_slaves("FLUSH SYSTEM")
            else:
                obj.hide_none()
        return func(master_order)
    return wrapper


@hide_non_executable
def menu(master_order):
    while True:
        master = master_order[-1]
        if not master.last:
            selection = run_selection(" ".join([x.short_name for x in master_order]), master.return_slaves_name())
            if selection == "TIMED OUT":
                sleep_and_wait()
                master_order = [main_menu]
            elif selection != "BACK":
                master_order.append(master.return_slave(selection))
            elif selection == "BACK" and master.name != "MAIN MENU":
                del master_order[-1]
        else:
            if master.slaves is None:
                print_to_display("SUCCESS")
                utime.sleep(1)
                master_order = yield master_order, master_order[-1].name
            else:
                sel = {key: None for key in [x[0] for x in master.slaves.values()]}
                for i in range(len(master.slaves)):
                    selection = run_selection(master.slaves[i][0], master.slaves[i][1])
                    if selection == "BACK":
                        print_to_display("FAILURE")
                        utime.sleep(1)
                        del master_order[-1]
                        break
                    elif selection == "TIMED OUT":
                        sleep_and_wait()
                    sel[master.slaves[i][0]] = selection
                else:
                    print_to_display("SUCCESS")
                    utime.sleep(1)
                    master_order = yield master_order, sel
        utime.sleep(0.05)
        menu(master_order)


def main():
    execute = dict(zip(["ADD POT", "ADD REFERENCE", "REMOVE SINGLE", "RUN", "REMOVE ALL", "FIND SENSOR", "FIND VALVE", "FLUSH SYSTEM"],
                       [pots.add_pot, pots.add_reference, pots.remove_pot, None, pots.reset_to_standard, pots.find_hsensor, pots.find_valve, pots.flush_system]))
    a = menu([main_menu])
    order, sel = next(a)
    while True:
        if order[-1].name == "RUN":
            sync = Sync_thread.SyncStateMachine(pots.return_pot_ids())
            sync.add_flag("input act", "State Machine")
            sync["all"] = True
            m = StateMachine(pots.pots, sel, sync)
            second_thread = _thread.start_new_thread(m.run_machine, ())
            input_activity(sync, pots)
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
    pots = Pots()
    end_time = ["20", "21", "22"]
    start_time = ["8", "9", "10", "11"]
    run_machine = MenuObject(name="RUN", short_name="RUN", slaves={0: ["Start Time", start_time],
                                                                   1: ["End Time", end_time]}, last=True)

    remove_single = MenuObject(name="REMOVE SINGLE", short_name="RSIN", slaves={0: ["ID", Pots.iden[0]]}, last=True)
    remove_all = MenuObject(name="REMOVE ALL", short_name="RALL", slaves=None, last=True)
    remove_pot = MenuObject(name="REMOVE POT", short_name="RPOT", slaves=[remove_single, remove_all])

    add_pot = MenuObject(name="ADD POT", short_name="APOT",
                         slaves={key: val for key, val in enumerate(zip(["ID", "Humidity", "Frequency", "Pot Size", "Actuator Pin", "Sensor Pin"],
                                                                        [Pots.iden[1], Pots.target_hum, Pots.frequency, Pots.pot_size, Pots.actuator_pin[1], Pots.sensor_pin[1]]))},
                         last=True)
    add_reference = MenuObject(name="ADD REFERENCE", short_name="AREF", slaves={0: ["ID", Pots.iden[1]], 1: ["Actuator Pin", Pots.actuator_pin[1]]}, last=True)
    add = MenuObject(name="ADD", short_name="ADD", slaves=[add_pot, add_reference])
    
    find_valve = MenuObject(name="FIND VALVE", short_name="FD VAL", slaves=None, last=True)
    find_sensor = MenuObject(name="FIND SENSOR", short_name="FD SEN", slaves=None, last=True)
    flush_system = MenuObject(name="FLUSH SYSTEM", short_name="FLSH SYS", slaves=None, last=True)
    
    find_hardware = MenuObject(name="FIND HARDWARE", short_name="FD HAWA", slaves=[find_sensor, find_valve, flush_system])
    main_menu = MenuObject(name="MAIN MENU", short_name="MAMU", slaves=[add, remove_pot, run_machine, find_hardware])
    main()
