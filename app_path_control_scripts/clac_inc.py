'''
用于标定倾角仪
'''
import time
from datetime import datetime
from Motor import Motor
from Inclinometer import Inclinometer
import os

def clac_inc(path="ClacOutput.txt"):
    m=Motor()
    inc=Inclinometer()
    m.cmd_find_zero()
    m.cmd_set_position(0.0)
    time.sleep(5)
    for i in range(5):
        inc._get_inc()
        # timestamp = time.time()
        # dt = datetime.fromtimestamp(timestamp)
        # formatted_time = dt.strftime("%H:%M:%S.%f")[:-3]
        # print(formatted_time)
    x_0,y_0=inc.current_inc_x,inc.current_inc_y


    m.cmd_set_position(180.0)
    time.sleep(5)
    for i in range(5):
        inc._get_inc()
        # timestamp = time.time()
        # dt = datetime.fromtimestamp(timestamp)
        # formatted_time = dt.strftime("%H:%M:%S.%f")[:-3]
        # print(formatted_time)

    x_180,y_180=inc.current_inc_x,inc.current_inc_y

    inc_x = (x_0 + x_180) / 2
    inc_y = (y_0 + y_180) / 2

    x = '0.0'
    y = '0.0'
    hz = '0.0'
    v = '0.0'
    if os.path.isfile(path):
        with open(path, "r") as f:
            line = f.readline()
            items = line.strip().split(",")
            if len(items) == 4:
                for item in items:
                    new_items = item.strip().split("=")
                    if new_items[0] == "x":
                        x = new_items[1]
                    elif new_items[0] == "y":
                        y = new_items[1]
                    elif new_items[0] == "hz":
                        hz = new_items[1]
                    elif new_items[0] == "v":
                        v = new_items[1]
    x="%.3f" %inc_x
    y="%.3f" %inc_y
    print(x,y)
    with open(path, "w") as f:
        f.writelines([f"x={x},y={y},hz={hz},v={v}"])
    return x,y


if __name__ == "__main__":
    clac_inc()