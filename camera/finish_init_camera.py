from time import sleep
time_delay=5

while True:
    camera_id=input("请输入恢复相机的ID：1 或者2 退出请输入x\n")
    if camera_id =="1" or camera_id =="2":
        # MENU=MENU+camera_id
        MENU ="/sys/dackey/menu%s"%(camera_id)
        OK = "/sys/dackey/ok%s"%(camera_id)
        DOWN = "/sys/dackey/down%s"%(camera_id)
        LEFT = "/sys/dackey/left%s"%(camera_id)
        RIGHT = "/sys/dackey/right%s"%(camera_id)
        UP = "/sys/dackey/up%s"%(camera_id)
        camera_power = "/sys/control/camera_power%s"%(camera_id)
        # camera2="/sys/control/camera_power2"
        power_camera = "/sys/control/power_camera%s"%(camera_id)
        cmd_keys=[OK,OK,OK,DOWN,OK,OK,DOWN,DOWN,OK,OK]
        button_usb_lists=[MENU,LEFT,LEFT,LEFT,LEFT,LEFT,OK,OK,MENU]
        # print(cmd_keys)
        #print("echo 1 > %s" % (camera_power))
        with open(camera_power,"w") as f:
            print("echo 1 > %s,开相机"%(camera_power))
            f.write("1")
            sleep(time_delay+2)
            f.close()

        with open(power_camera,"w") as f:
            print("echo 0 > %s，关闭usb充电"%(power_camera))
            f.write("0")
            sleep(time_delay)
            f.close()

        for cmd_key in cmd_keys:
            with open(cmd_key,"w") as f:
                print("echo 1 > %s"%(cmd_key))
                f.write("1")
                sleep(time_delay)
                f.close()

        for button_usb_list in button_usb_lists:
            with open(button_usb_list,"w") as f:
                print("echo 1 > %s"%(button_usb_list))
                f.write("1")
                sleep(time_delay)
                f.close()

        with open(power_camera,"w") as f:
            print("echo 1 > %s"%(power_camera))
            f.write("1")
            sleep(time_delay)
            f.close()
    elif camera_id =="x":
        break
    else:

        continue

