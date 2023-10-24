# Linux commands to mount Bluetooth HC-05 as serial output
# find id with bluetoothctl
# power on
# agent on
# scan on
# sudo killall rfcomm
# sudo rfcomm connect /dev/rfcomm0 {device address} 1 &
# screen /dev/rfcomm0 9600 (for printing into screen - Ctrl-A, k, y to kill - but screen occupied
import asyncio
import random
import time
from datetime import datetime
import numpy as np
import serial
import warnings
from collections import deque
import threading
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from matplotlib.animation import FuncAnimation

LEN = 100


class SerialPlotter:

    def __init__(self, initialized_event: threading.Event):
        self.ser = serial.Serial("/dev/rfcomm0", 9600, timeout=1)
        self.keys = []
        self.queues = list[deque]
        self.timestamps = deque(maxlen=LEN)
        self.initialized_event = initialized_event
        self.water_queues = list[deque]
        self.pot_indices = list()
        self.initialized = False

    def read_time(self, *data):
        print("time", end=": ")
        print(data)

    def read_init(self, *data):
        print("initialized")
        if self.keys != data and self.keys:
            warnings.warn("New keys. Need to reinit everything?")

        self.pot_indices = [x.split()[1] for x in sorted([item for item in data if "pot" in item.lower()])]
        self.water_queues = [deque(maxlen=1000) for _ in self.pot_indices]
        self.initialized_event.set()
        self.keys = data
        self.queues = [deque(maxlen=LEN) for _ in self.keys]
        self.initialized = True

    def read_data(self, *data):
        if not self.initialized:
            return
        for queue, n_data in zip(self.queues, data):
            try:
                n_data = float(n_data)
            except ValueError:
                n_data = float(n_data[:-len(n_data.lstrip("0123456789."))])
            queue.append(n_data)
        self.timestamps.append(datetime.now())
        print(data)

    def read_water(self, *data):
        if not self.initialized:
            return
        # ('water', '2', 1.08)
        self.water_queues[self.pot_indices.index(data[0])].append((datetime.now(), data[1]))

    def main(self):
        with self.ser as ser:
            ser.isOpen()
            while True:
                raw_data = ser.readline().decode().strip()
                if raw_data == "":
                    warnings.warn("Disconnected?")
                    continue
                if raw_data[0] != "(":
                    continue
                raw_data = eval(raw_data)
                match raw_data[0]:
                    case "time":
                        self.read_time(*raw_data[1:])
                    case "init":
                        self.read_init(*raw_data[1:])
                    case "data":
                        # what's with time raw_data[1]?
                        self.read_data(*raw_data[2:])
                    case "water":
                        self.read_water(*raw_data[1:])


class DummySerialReader:

    def __init__(self, initialized_event):
        self.timestamps = deque(maxlen=LEN)
        self.queues = list[deque]
        self.initialized_event = initialized_event
        self.keys = ('Pot 2 hum', 'Pot 1 hum', 'rel hum', 'Temp', 'Pressure', 'Pot 3 hum')
        self.queues = [deque(maxlen=LEN) for _ in self.keys]
        self.water_queues = [deque(maxlen=1000) for _ in range(3)]

    async def read_data(self, stop_event: asyncio.Event):
        self.initialized_event.set()
        while not stop_event.is_set():
            for i, que in enumerate(self.queues):
                que.append(random.random() * (i + 1))
            self.timestamps.append(datetime.now())
            await asyncio.sleep(0.5)

    async def read_water_events(self, stop_event: asyncio.Event, index):
        while not stop_event.is_set():
            await asyncio.sleep(random.random() * 10)
            self.water_queues[index].append((datetime.now(), 0.5))

    def main(self):
        loop = asyncio.new_event_loop()
        stop_event = asyncio.Event()
        tasks = [loop.create_task(self.read_data(stop_event))]
        for i in range(3):
            tasks.append(loop.create_task(self.read_water_events(stop_event, i)))
        try:
            loop.run_forever()
        except KeyboardInterrupt:
            stop_event.set()
            for task in tasks:
                if not task.done() or task.cancelled():
                    loop.run_until_complete(task)


class Plotter:

    def __init__(self):
        self.lines = list()
        self.water_lines = list()
        self.axs = np.ndarray
        self.ax2 = list()
        self.new_order = list()

    def draw_plot(self, sp: SerialPlotter or DummySerialReader, initialized_event: threading.Event):
        while not initialized_event.is_set():
            time.sleep(0.5)
        fig, self.axs = plt.subplots(len(sp.keys), sharex=True)
        plt.xticks(rotation=90)
        self.new_order = sorted(range(len(sp.keys)), key=lambda k: sp.keys[k])
        self.lines = [[] for _ in sp.keys]
        for i, ax in zip(self.new_order, self.axs):
            key = sp.keys[i]
            if "pot" in key.lower():
                ax2 = ax.twinx()
                ax2.set_ylim(0, 2)
                self.water_lines.append(*ax2.plot([], [], "bo", c="orange"))
                self.ax2.append(ax2)
            ax.set_ylim(-1, 1)
            self.lines[i] = ax.plot([], [], label=key)[0]
            ax.xaxis.set_major_formatter(mdates.DateFormatter("%H:%M:%S"))
            ax.legend(loc="upper right")
        ani = FuncAnimation(fig, self.animate, fargs=(sp, ), interval=1000, cache_frame_data=False)
        plt.show()

    def animate(self, _, sp: SerialPlotter):
        for line, que, ax in zip(self.lines, sp.queues, [self.axs[i] for i in self.new_order]):
            if not len(sp.timestamps) < 2:
                ax.set_xlim(sp.timestamps[0], sp.timestamps[-1])
                data = list(que)
                line.set_data(sp.timestamps, data)
                ax.set_ylim(min(data) - 0.5 * max(data), max(data) + 0.5 * max(data))
        for line, que in zip(self.water_lines, sp.water_queues):
            try:
                dates, amount = zip(*que)
                line.set_data(dates, amount)
            except ValueError:
                pass
        return self.lines


if __name__ == "__main__":
    init_event = threading.Event()
    # init_event.set()
    splot = DummySerialReader(init_event)
    t1 = threading.Thread(target=splot.main, daemon=True)
    t1.start()
    p = Plotter()
    p.draw_plot(splot, init_event)

