# Linux commands to mount Bluetooth HC-05 as serial output
# find id with bluetoothctl
# power on
# agent on
# scan on
# sudo killall rfcomm
# sudo rfcomm connect /dev/rfcomm0 {device address} 1 &

import serial
import os
from functools import wraps
import requests
import datetime
from datetime import timedelta


def get_filename(func):
    @wraps(func)
    def wrapper(self, *args, **kwargs):
        date = dict.fromkeys(["day", "month", "year"], 0)
        i = 0
        if os.path.exists(self.path):
            if self.data[0][:4] == "TIME":
                for i, sample in enumerate(self.data[1:]):
                    key, val = sample.split(":")
                    date[key] = val.split(",")[0]
                    if all(date.values()):
                        break
                filename = "data{day}_{month}_{year}.csv".format(day=date["day"],
                                                                 month=date["month"],
                                                                 year=date["year"])
                return func(self, filename, i + 2, *args, **kwargs)
            else:
                raise ValueError("First Item not Time --> Can't process filename")
        else:
            raise ValueError("Path does not exist --> awaiting init file ")

    return wrapper


def read_weather_forcast(*args):
    if args == () or args is None:
        args = ["HeatIndexC", "cloudcover", "humidity", "precipMM",
                "pressure", "tempC", "winddirDegree", "windspeedKmph"]
    # cur_time = (date + timedelta(hours=20)).hour * 100 for simulation
    cur_time = datetime.datetime.now().hour * 100
    data = {}
    for day in range(3):
        for hour_data in requests.get("https://wttr.in/Cologne?format=j1").json()["weather"][day]["hourly"]:
            forecast_time = int(hour_data["time"])
            forecast_time += 2400 * day
            if not forecast_time or cur_time // forecast_time:
                # only read forecast data, not forecast in current time
                continue
            timestep_data = {}
            for arg in args:
                timestep_data[arg] = hour_data[arg]
            data[forecast_time] = timestep_data
    return data


class DataCollector:
    def __init__(self, serial_address):
        self.type = None
        self.serial_address = serial_address
        self.data = []
        self.collector_count = 1
        self.path = "Collected_data/1/"
        self.forecast_data = None

    def read_type(self):
        with serial.Serial(self.serial_address, 9600, timeout=1) as ser:
            while True:
                line = ser.readline().decode("UTF-8").strip()
                if line == "init file":
                    self.type = self.write_init
                    self.collect_data()
                elif line == "write data":
                    self.type = self.write_data
                    self.collect_data()

    def collect_data(self):
        self.data = []
        with serial.Serial(self.serial_address, 9600, timeout=1) as ser:
            while (line := ser.readline().decode("UTF-8").strip()) != "end":
                self.data.append(line)
            self.type()

    def write_init(self):
        while os.path.exists(self.path):
            self.collector_count += 1
            self.path = "Collected_data/{}/".format(self.collector_count)
        os.makedirs(self.path)
        with open(self.path + "init_file.txt", "w") as file:
            for sample in self.data:
                file.write(sample + "\r\n")

    @get_filename
    def write_data(self, filename, start_index):
        with open(self.path + filename, "a+") as file:
            for sample in self.data[start_index:]:
                if sample[:4] == "DATA":
                    continue
                file.write(sample)
            file.write("\r\n")
        print(read_weather_forcast())


if __name__ == "__main__":
    # DataCollector("/dev/rfcomm0").read_type()
    print(read_weather_forcast())
