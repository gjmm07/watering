import time
from collections import deque
import threading
from datetime import datetime


data = [
    ('init', 'Pot 2 hum', 'Pot 1 hum', 'rel hum', 'Temp', 'Pressure', 'Pot 3 hum'),
    ('setup', (3, [('hum', 'MEDIUM'), ('size', 'MEDIUM'), ('freq', 'MEDIUM')]),
     (1, [('hum', 'MEDIUM'), ('size', 'MEDIUM'), ('freq', 'MEDIUM')]),
     (2, [('hum', 'MEDIUM'), ('size', 'MEDIUM'), ('freq', 'MEDIUM')])),
    ('data', 0.6148439, 0.5907225, '51.96%', '22.45C', '1006.34hPa', 0.3675624),
    ('data', 0.6132326, 0.5907225, '51.95%', '22.45C', '1006.34hPa', 0.3637537),
    ('data', 0.6197787, 0.594287, '51.96%', '22.45C', '1006.33hPa', 0.3628748),
    ('data', 0.6177737, 0.5922361, '51.98%', '22.45C', '1006.31hPa', 0.3638514),
    ('data', 0.6106447, 0.5920409, '52.00%', '22.45C', '1006.29hPa', 0.36766),
    ('data', 0.6106966, 0.5940429, '51.99%', '22.46C', '1006.33hPa', 0.363949),
    ('data', 0.6209537, 0.5990234, '51.99%', '22.45C', '1006.34hPa', 0.3643885),
    ('data', 0.6165041, 0.5914549, '51.98%', '22.46C', '1006.36hPa', 0.3621424),
    ('data', 0.6168978, 0.5994141, '51.95%', '22.46C', '1006.27hPa', 0.3637537),
    ('data', 0.6141603, 0.5915526, '51.95%', '22.46C', '1006.29hPa', 0.3647303),
    ('data', 0.6192386, 0.5864256, '51.97%', '22.47C', '1006.34hPa', 0.3659022),
    ('init', 'Pot 2 hum', 'Pot 1 hum', 'rel hum', 'Temp', 'Pressure', 'Pot 3 hum'),
    ('setup', (3, [('hum', 'MEDIUM'), ('size', 'MEDIUM'), ('freq', 'MEDIUM')]),
     (1, [('hum', 'MEDIUM'), ('size', 'MEDIUM'), ('freq', 'MEDIUM')]),
     (2, [('hum', 'MEDIUM'), ('size', 'MEDIUM'), ('freq', 'MEDIUM')])),
    ('data', 0.6184573, 0.5848631, '51.95%', '22.45C', '1006.31hPa', 0.3665858),
    ('data', 0.6129915, 0.5979004, '51.96%', '22.45C', '1006.29hPa', 0.3628748),
    ('data', 0.6202243, 0.5923827, '51.99%', '22.46C', '1006.24hPa', 0.365951),
    ('data', 0.6133791, 0.5964355, '51.99%', '22.47C', '1006.25hPa', 0.3665858),
    ('data', 0.6143557, 0.5921874, '51.99%', '22.46C', '1006.32hPa', 0.3675136),
    ('data', 0.6186526, 0.5902342, '51.98%', '22.45C', '1006.29hPa', 0.3618982),
    ('data', 0.6190921, 0.5907713, '51.95%', '22.46C', '1006.30hPa', 0.3669276),
    ('data', 0.6138704, 0.5884764, '51.97%', '22.46C', '1006.24hPa', 0.3689784),
    ('data', 0.6157229, 0.6002441, '51.97%', '22.46C', '1006.30hPa', 0.3674159),
    ('data', 0.6165071, 0.5874997, '51.97%', '22.46C', '1006.22hPa', 0.3607264),
    ('data', 0.6121126, 0.5881834, '51.94%', '22.47C', '1006.34hPa', 0.3664882),
    ('data', 0.6182162, 0.59375, '51.95%', '22.45C', '1006.29hPa', 0.365951),
    ('data', 0.6136263, 0.5873533, '51.95%', '22.45C', '1006.31hPa', 0.3654139),
    ('data', 0.6222659, 0.5967772, '51.94%', '22.46C', '1006.30hPa', 0.3672206),
    ('data', 0.6150881, 0.5959472, '51.95%', '22.45C', '1006.26hPa', 0.3657069),
    ('data', 0.6182651, 0.5872068, '51.95%', '22.46C', '1006.26hPa', 0.3692714)
]


class HumControl:

    def __init__(self):
        self.keys = tuple()
        self.data = list[deque[float]]
        self.setup = tuple
        self.save_counter = 0
        self.timestamps = []
        self.filename = "0"

    def init(self, keys):
        if keys != self.keys:
            self.keys = keys
            self.data = [deque(maxlen=100) for _ in keys]
            self.init_file()

    def pot_setup(self, setup_vals):
        if setup_vals != self.setup:
            self.setup = setup_vals
            ques = [self.data[i] for i, key in enumerate(self.keys) for setup in self.setup if str(setup[0]) in key]
            threading.Thread(target=analyze_data, args=(ques, self.setup), daemon=True).start()

    def append_data(self, read_data):
        line = []
        for d, que in zip(read_data, self.data):
            if type(d) is str:
                d = float(str().join(c for c in d if c.isdigit() or c == "."))
            que.append(d)
            line.append(str(d))
        self.save_data(", ".join(line + [datetime.now().strftime("%Y-%M-%d %H:%m:%S")]) + "\n")

    def save_data(self, line):
        with open(self.filename + ".txt", mode="a") as f:
            f.write(line)
            if self.save_counter > 10:
                self.save_counter = 0
                self.init_file()
            self.save_counter += 1

    def init_file(self):
        self.filename = str(int(self.filename) + 1)
        with open(self.filename + ".txt", mode="w") as f:
            f.write(", ".join(self.keys + ("timestamp", )))
            f.write("\n")


def analyze_data(queues, pot_info):
    print(pot_info)
    while True:
        print(queues)
        time.sleep(10)


def reader():
    fdata = iter(data)
    while True:
        yield next(fdata)
        time.sleep(2)


def main():
    r = reader()
    hc = HumControl()
    while True:
        try:
            rdata = next(r)
            match rdata[0]:
                case "init":
                    hc.init(rdata[1:])
                case "setup":
                    hc.pot_setup(rdata[1:])
                case "data":
                    hc.append_data(rdata[1:])
        except RuntimeError:
            break


if __name__ == "__main__":
    main()
    print()
