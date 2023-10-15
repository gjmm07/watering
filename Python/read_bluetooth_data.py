# Linux commands to mount Bluetooth HC-05 as serial output
# find id with bluetoothctl
# power on
# agent on
# scan on
# sudo killall rfcomm
# sudo rfcomm connect /dev/rfcomm0 {device address} 1 &
# screen /dev/rfcomm0 9600 (for printing into screen - Ctrl-A, k, y to kill - but screen occupied
import random
import time
from datetime import datetime
import serial
import warnings
from collections import deque
import threading
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation

LEN = 100


class SerialPlotter:

    def __init__(self, initialized_event: threading.Event):
        self.ser = serial.Serial("/dev/rfcomm0", 9600, timeout=1)
        self.keys = []
        self.queues = list[deque]
        self.timestamps = deque(maxlen=LEN)
        self.initialized_event = initialized_event

    def read_time(self, *data):
        print("time", end=": ")
        print(data)

    def read_init(self, *data):
        print("initialized")
        if self.keys != data and self.keys:
            warnings.warn("New keys. Need to reinit everything?")
        self.initialized_event.set()
        self.keys = data
        self.queues = [deque(maxlen=LEN) for _ in self.keys]

    def read_data(self, *data):
        if not self.keys:
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
        print("read water", end="")
        print(data)

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


PLOTS = 5


class DummySerialReader:

    def __init__(self, initialized_event):
        self.timestamps = deque(maxlen=LEN)
        self.queues = list[deque]
        self.initialized_event = initialized_event
        self.keys = []

    def main(self):
        self.queues = [deque() for _ in range(PLOTS)]
        self.keys = ["a" for _ in self.queues]
        self.initialized_event.set()
        while True:
            for que in self.queues:
                que.append(random.random())
            self.timestamps.append(datetime.now())
            time.sleep(0.5)


class Plotter:

    def __init__(self):
        self.lines = list()

    def draw_plot(self, sp: SerialPlotter or DummySerialReader, initialized_event: threading.Event):
        while not initialized_event.is_set():
            time.sleep(0.5)
        fig, axs = plt.subplots(len(sp.keys))
        for ax in axs:
            ax.set_xlim((0, LEN))
            ax.set_ylim(-1, 1)
            self.lines.append(*ax.plot([], []))
        ani = FuncAnimation(fig, self.animate, fargs=(sp, ), interval=25)
        plt.show()

    def animate(self, _, sp: SerialPlotter):
        for line, que in zip(self.lines, sp.queues):
            print(sp.timestamps)
            line.set_data(range(len(sp.timestamps)), list(que))
        return self.lines


if __name__ == "__main__":
    init_event = threading.Event()
    # init_event.set()
    splot = DummySerialReader(init_event)
    t1 = threading.Thread(target=splot.main, daemon=True)
    t1.start()
    p = Plotter()
    p.draw_plot(splot, init_event)

