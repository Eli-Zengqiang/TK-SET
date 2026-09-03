from time import sleep
time_delay=10
n=0
camera_power = "/sys/control/camera_power2"
while True:
    with open(camera_power, "w") as f:
        print(f"echo 1 > {camera_power}")
        f.write("1")
        sleep(time_delay)
        f.close()
        n=n+1
        print(n)
        if n >=30:
            break
