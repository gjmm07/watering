import sys
import utime
from rotaryIRQ import RotaryIRQ
from buttons_IRQ import ButtonsIRQ
import Menu
from pots import Pots
from WateringRun import AsyncRunner
import SpecialFuncs
from Hardware import LCDDisplay



def process_backwards(history, menu):
    if len(history) >= 2:
        # history, menu = process_backwards(history, menu)
        history.pop(-1)
        menu = history[-1]
        menu.initialize()
    return history, menu


def process_select(history, menu, collector): 
    key, menu = menu.select()
    if isinstance(menu, Menu.CollectorMenu): # latest collector in the tree
        collector = menu
        
    if isinstance(menu, Menu.Menu): # if selection is a menu object - simply run the menu
        history.append(menu)
        if menu.slaves: # if it has salves run the menu
            menu.initialize()
        else: # if no slaves present call function and go backwards
            collector.function(*collector.func_args)
            history, menu = process_backwards(history, menu)
            collector = None
        
    else: # handle cases where selection isn't another menu
        selection = menu
        collector.collect_data(key, selection)
        if collector.ready_to_exe:
            res = collector.function(*collector.func_args, **collector.kwargs)
            if res is not None:
                collector.show_short(res, 1)
#             if collector.bsteps_on_done is None:
#                 
#                 collector = None
#             else:
            print(history)
            print(menu)
            if collector.bsteps_on_done is None or abs(collector.bsteps_on_done) > len(history):
                history, menu = [history[0]], history[0]
            else:
                history = history[:(collector.bsteps_on_done + 1) if collector.bsteps_on_done != -1 else None]
                menu = history[-1]
                
            menu.initialize()
        else:
            history, menu = process_backwards(history, menu)
    return history, menu, collector


def sleep():
    LCDDisplay().backlight_off()
    val = r.value()
    while not (back.pressed() or select.pressed() or val != 0):
        utime.sleep(0.2)
        val = r.value()
    r.reset()
    LCDDisplay().backlight_on()
        


def main():
    
    history = []
    
    collector = None
    
    menu = main_menu
    history.append(menu)
    menu.initialize()
    
    start = utime.ticks_ms()
    
    while True:
        val = r.value()
        if back.pressed():
            history, menu = process_backwards(history, menu)
            start = utime.ticks_ms()
        
        elif select.pressed():
            history, menu, collector = process_select(history, menu, collector)
            start = utime.ticks_ms()
        
        elif val != 0:
            menu.increment(val)
            r.reset()
            start = utime.ticks_ms()
        
        if utime.ticks_diff(utime.ticks_ms(), start) > 15000:
            sleep()
            start = utime.ticks_ms()
            



if __name__ == "__main__":
    
    # ______ init classes _________
    
    
    r = RotaryIRQ(pin_num_clk=11,
                  pin_num_dt=12,
                  reverse=True,
                  range_mode=RotaryIRQ.RANGE_WRAP)
    
    back = ButtonsIRQ(22)
    select = ButtonsIRQ(10)
    
    pots = Pots()
    async_runner = AsyncRunner(pots.pots, back, r)
    
    pot_senp = Menu.Menu("Sensor Pin", "SP", pots.sen_pin[1], key="sen_pin")
    pot_actp = Menu.Menu("Actuator Pin", "AP", pots.act_pin[1], key="act_pin")
    pot_size = Menu.Menu("Pot Size", "PS", pots.SIZE, key="size")
    pot_frequency = Menu.Menu("Pot Frequency", "PF", pots.FREQUENCY, key="freq")
    pot_humidity = Menu.Menu("Pot Humidity", "PH", pots.HUMIDITY, key="hum")
    pot_index = Menu.Menu("Pot Index", "PI", pots.indices[1], key="ind")
    add_pot = Menu.CollectorMenu("Add Pot", "AP", [pot_index, pot_humidity, pot_frequency, pot_size,
                                              pot_senp, pot_actp], function=pots.add_pot)
    
    remove_single = Menu.CollectorMenu("Remove Single", "RS", pots.indices[0], function=pots.remove_pot, key="ind")
    remove_all = Menu.CollectorMenu("Remove All", "RA", None, function=pots.remove_all)
    
    remove_pot = Menu.Menu("Remove Pot", "RP", [remove_all, remove_single])
    
    run_machine = Menu.CollectorMenu("Run Machine", "RM", None, function=async_runner.main)
    current_setup = Menu.CollectorMenu("Display Setup", "DS", None, function=pots.display_setup)
    
    find_valve = Menu.CollectorMenu("Find Valve",
                                    "FV",
                                    pots.act_pin[1].copy(),
                                    SpecialFuncs.find_valve,
                                    pot_actp,
                                    pots,
                                    bsteps_on_done = -1,
                                    key="act_pin")
    
    find_sensor = Menu.CollectorMenu("Find Sensor",
                                     "FS",
                                     pots.sen_pin[1].copy(),
                                     SpecialFuncs.find_sensor,
                                     pot_senp,
                                     pots,
                                     bsteps_on_done = -1, 
                                     key="sen_pin")
    
    flush_system = Menu.CollectorMenu("Flush System",
                                      "FS",
                                      None,
                                      SpecialFuncs.flush_sys,
                                      pots.act_pin[0])
    
    pots.add_pot(1, Pots.HUMIDITY[0], Pots.FREQUENCY[0], Pots.SIZE[0], "E", "B")
    pots.add_pot(2, Pots.HUMIDITY[0], Pots.FREQUENCY[0], Pots.SIZE[0], "A", "F")
    pots.add_pot(3, Pots.HUMIDITY[0], Pots.FREQUENCY[0], Pots.SIZE[0], "G", "C")
    
    print(find_sensor.key)
    
    special_funcs = Menu.Menu("Special Funcs", "SF", (find_valve, find_sensor, flush_system))
    
    main_menu = Menu.Menu("main_menu", "mm", [add_pot, remove_pot, run_machine, current_setup, special_funcs])
    try:
        main()
    except KeyboardInterrupt:
        LCDDisplay().backlight_off()

    