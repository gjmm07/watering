import uasyncio as asyncio
from machine import Pin, I2C
from machine_i2c_lcd import I2cLcd
from collections import deque, OrderedDict
import random
from async_queue import Queue, QueueEmpty # not jet included in offical uasyncio ??
from buttons_IRQ import ButtonsIRQ
from rotaryIRQ import RotaryIRQ
import utime
import Hardware



# Initialisierung I2C
i2c = I2C(0, sda=Pin(20), scl=Pin(21), freq=100000)

# Initialisierung LCD über I2C
lcd = I2cLcd(i2c, 0x27, 2, 16)

def _empty_deque(queue):
    data = []
    while True:
        # stupid implementation due to deque in micropython
        try:
            data.append(queue.popleft())
        except IndexError:
            return data


class AsyncRunner:
    
    HUM_LOOKUP = {"WET": 0.75,
                  "MEDIUM": 0.4,
                  "DRY": 0.2}
    
    FREQUENCY_LOOKUP = {"OFTEN": 10,
                        "MEDIUM": 50,
                        "RARLY": 20}
    
    SIZE_LOOKUP = {"HUGE": 2,
                   "BIG": 1.5,
                   "MEDIUM": 1,
                   "SMALL": 0.2}
    
    def __init__(self, pots: dict, back_button: ButtonsIRQ, rotary: RotaryIRQ):
        self.pots = pots
        self.stop_event = asyncio.Event()
        self.pump_event = asyncio.Event()
        self.watered_event = asyncio.Event()
        self.loop = asyncio.get_event_loop()
        self.back_button = back_button
        self.rotary = rotary
        self.display_data = OrderedDict([("Temp", 0), ("rel hum", 0), ("Pressure", 0)])
        for name in pots.keys():
            self.display_data["Pot {} hum".format(name)] = 0
        Hardware.Valve().close()
    
    def main(self):
        tasks = []
        water_queue = deque((), 100)
        log_queue = Queue()
        
        for i, value in self.pots.items():
            last_recordings = deque((), 100)
            tasks.append(self.loop.create_task(self.measure(last_recordings, log_queue, i)))
            tasks.append(self.loop.create_task(self.analyse_humidity(i, last_recordings, water_queue)))
        
        tasks.append(self.loop.create_task(self.analyse_outside_cond(log_queue)))
        tasks.append(self.loop.create_task(self.write_events(log_queue)))
        tasks.append(self.loop.create_task(self.water_pots(water_queue, log_queue)))
        tasks.append(self.loop.create_task(self.display()))
        self.loop.run_forever()
        for task in tasks:
            if not task.done():
                self.loop.run_until_complete(task)
        Hardware.LCDDisplay().off()
        Hardware.Valve().close()
        Hardware.Pump().off()
        print("shutdown everything")
        
    def _measure_humidity(self, name):
        """ Return the pots humidtiy"""
        return Hardware.HumSensor().read(self.pots[name]["sen_pin"])
    
    async def process_sleep_long(self, sleep_time):
        for _ in range(sleep_time):
            if self.stop_event.is_set():
                break
            await asyncio.sleep(1)
    
    async def watering_done(self):
        while self.pump_event.is_set():
            await asyncio.sleep(1)
                                           
    async def analyse_outside_cond(self, log_queue):
        while not self.stop_event.is_set():
            outside_conditions = Hardware.ConditionSensor().read()
            for key, val in outside_conditions.items():
                self.display_data[key] = val
                log_queue.put_nowait((key, val))
            await asyncio.sleep(0.5)
        
    async def measure(self, last_recordings, log_queue, name):
        while not self.stop_event.is_set():
            msrt = []
            for _ in range(5):
                msrt.append(self._measure_humidity(name))
                await asyncio.sleep(0.1)
                await self.watering_done()
            hum = sum(msrt) / len(msrt)
            self.display_data["Pot {} hum".format(name)] = hum
            log_queue.put_nowait(("Pot {} hum".format(name), hum))
            last_recordings.append(hum)
            
    async def analyse_humidity(self, name, hum_queue, water_queue):
        hum_threshold = self.HUM_LOOKUP[self.pots[name]["hum"]]
        sleep_time = self.FREQUENCY_LOOKUP[self.pots[name]["freq"]]
        while not self.stop_event.is_set():
            longsleep_ready = False
            await self.process_sleep_long(sleep_time)
            while True:
                await asyncio.sleep(5)
                data = _empty_deque(hum_queue)
                if self.pump_event.is_set():
                    _ = _empty_deque(hum_queue)
                    continue
                if not data:
                    continue
                if sum(data) / len(data) < 0.2:
                    print("enqueue", name)
                    water_queue.append(name)
                    longsleep_ready = True
                elif longsleep_ready:
                    break
                
    async def _apply_water(self, name, valve_open_time):
        print("start pump")
        self.pump_event.set()
        # Hardware.Pump().on() # during pumping measure pot humidity is not possible 
        await asyncio.sleep(1)  # build up pressure
        print("open", self.pots[name]["act_pin"])
        Hardware.Valve().open_(self.pots[name]["act_pin"])
        await asyncio.sleep(valve_open_time)
        
    async def water_pots(self, water_queue, log_queue):
        while not self.stop_event.is_set():
            await self.process_sleep_long(120) # deep sleep
            while not self.stop_event.is_set():
                to_water = set(_empty_deque(water_queue))
                if to_water:
                    for water_pot in to_water:
                        vot = self.SIZE_LOOKUP[self.pots[water_pot]["size"]] * self.HUM_LOOKUP[self.pots[water_pot]["hum"]]
                        await self._apply_water(water_pot, vot)
                        log_queue.put_nowait(("water" + str(water_pot), 1))
                    Hardware.Valve().close()
                    Hardware.Pump().off()
                    print("sleep ADC Normalization")
                    await asyncio.sleep(10)
                    print("done ADC Normalization")
                    self.pump_event.clear()
                    await asyncio.sleep(4) # light sleep
                else:
                    # No pots to water
                    break
                
    def _check_bounds(self, len_, val):
        if val < 0:
            return len_ - 1
        elif val >= len_:
            return 0
        return val
                
    async def display(self):
        start_time = utime.time()
        counter = 0
        keys = list(self.display_data.keys())
        lcd.backlight_on()
        while not self.back_button.pressed():
            await asyncio.sleep(0.5)
            val = self.rotary.value()
            
            if val != 0:
                counter += val
                r.reset()
                start_time = utime.time()
            counter = self._check_bounds(len(keys), counter)
            lcd.clear()
            lcd.putstr(keys[counter] + str(self.display_data[keys[counter]]))
            if utime.time() - start_time > 20:
                await self.display_sleep()
                start_time = utime.time()
                
        print("stop")
        self.stop_event.set()
        self.loop.stop()
        
    async def display_sleep(self):
        lcd.backlight_off()
        lcd.clear()
        while not self.back_button.pressed():
            await asyncio.sleep(0.5)
        lcd.backlight_on()
                
    def _get_current_time(self):
        return utime.localtime()[:-2]
    
    def return_empty_write(self):
        write_vals = {key: None for key in self.display_data.keys()}
        for key in self.pots.keys():
            write_vals["water" + str(key)] = 0
        return write_vals
            
            
    async def write_events(self, queue):
        write_vals = self.return_empty_write()
        Hardware.BluetoothWriter().write(*write_vals.keys())
        time = self._get_current_time()
        Hardware.BluetoothWriter().write(*time)
        start = utime.ticks_ms()
        while not self.stop_event.is_set():
            key, val = await queue.get()
            write_vals[key] = val
            if all(val is not None for val in write_vals.values()):
                if time[-4] != (time:=self._get_current_time())[-4]:
                    # new day
                    Hardware.BluetoothWriter().write(*time)
                    start = utime.ticks_ms()
                Hardware.BluetoothWriter().write(utime.ticks_diff(utime.ticks_ms(), start), *write_vals.values())
                write_vals = self.return_empty_write()
                    
        
            
if __name__ == "__main__":
    Hardware.LCDDisplay().backlight_off()
    
    pots = {1: {'freq': 'MEDIUM', 'act_pin': 'B', 'hum': 'MEDIUM', 'size': 'MEDIUM', 'sen_pin': 'E'},
            2: {'freq': 'MEDIUM', 'act_pin': 'F', 'hum': 'MEDIUM', 'size': 'MEDIUM', 'sen_pin': 'A'},
            3: {'freq': 'MEDIUM', 'act_pin': 'C', 'hum': 'MEDIUM', 'size': 'MEDIUM', 'sen_pin': 'G'}}
    
    back = ButtonsIRQ(22)
    r = RotaryIRQ(pin_num_clk=11,
                  pin_num_dt=12,
                  reverse=True,
                  range_mode=RotaryIRQ.RANGE_WRAP)
    try:  
        AsyncRunner(pots, back, r).main()
    except KeyboardInterrupt:
        pass
    
    Hardware.Pump().off()
    Hardware.LCDDisplay().backlight_off()
    
    
    
    