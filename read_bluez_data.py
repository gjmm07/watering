import serial
import os


def write_init_file(data, *_):
    print("write init file")
    new_path = "Collected_data/1/"
    counter = 1
    while os.path.exists(new_path):
        counter += 1
        new_path = "Collected_data/{}/".format(counter)
    print(new_path)
    os.makedirs(new_path)
    pot_counter = 0
    with open(new_path + "init_file.txt", "w") as file:
        for item in data:
            file.write(item + "\r\n")
    return new_path, pot_counter


def write_data(data, path, pot_counter):
    print("write data")
    date = {"year": None, "month": None, "day": None}
    filename = ""
    for item in data:
        key, val = item.split(":")
        if key in date.keys():
            date[key] = val
        if all([x is not None for x in list(date.values())]):
            filename = "data{day}_{month}_{year}.csv".format(day=date["day"].strip(),
                                                             month=date["month"].strip(),
                                                             year=date["year"].strip())
            break
    with open(path + filename, "a+") as file:
        file.write(",".join(data))


with serial.Serial('/dev/rfcomm0', 9600, timeout=1) as ser:
    state = ""
    handlers = {"init file": write_init_file, "write data": write_data}
    data = []
    path, pot_counter = None, None
    while True:
        if line := ser.readline().decode("UTF-8").strip():
            print(line)
            if line == "write data":
                state = line
            elif line == "init file":
                state = line
            elif line == "end":
                print("reached")
                print(state)
                handlers[state](data, path, pot_counter)
                data = []
            else:
                data.append(line)

