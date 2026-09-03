import subprocess
import requests
import time
import re
import os
def kill_app_process():
    '''
    关闭app进程
    :return:
    '''
    command = "ps -A | grep app"
    process = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    stdout = str(process.communicate())
    print(stdout)
    stdout0 = stdout.strip().split()
    command1 = rf"kill -9 {stdout0[1]}"
    print(command1)
    process1 = subprocess.Popen(command1, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    stdout1 = process1.communicate()

def write_configurated_files():
    #写入etc路径下的shutdown.sh，bftpd.conf
    print("#######################复制etc路径中的文件#######################")
    command1 = "unzip -o -j 'configuration_files.zip' 'etc/*' -d /etc"  #command1 = "unzip -o -j 'configuration_files.zip' 'etc/*' -d /etc"
    process1=subprocess.Popen(command1, shell=True, stdout=subprocess.PIPE,stdin=subprocess.PIPE,stderr=subprocess.PIPE)
    stdout1,stderr1=process1.communicate()
    if process1.returncode==0:
        print("\n成功解压并拷贝etc路径文件\n")
    else:
        print(stderr1)
        print("\n解压并拷贝etc路径文件失败\n")

    print("#######################复制app路径中的文件#######################")
    #写入app路径下的所有python文件，power_on_all.sh等
    command2="unzip -o -j 'configuration_files.zip' 'app/*' -d /app/"
    #command2="unzip -o -j 'configuration_files.zip' 'app路径/*' -d /app"
    process2=subprocess.Popen(command2, shell=True, stdout=subprocess.PIPE,stdin=subprocess.PIPE,stderr=subprocess.PIPE)
    stdout2,stderr2=process2.communicate()
    if process2.returncode==0:
        print("\n成功解压并拷贝app路径文件\n")
    else:
        print(stderr2)
        print("\n解压并拷贝app路径文件失败\n")

    print("#######################复制etc_systemd路径中的文件#######################")
    #写入systemd路径下的日志配置文件journald.conf
    command3="unzip -o -j 'configuration_files.zip' 'etc_systemd/*' -d /etc/systemd"
    #command3="unzip -o -j 'configuration_files.zip' 'etc_systemd/*' -d /etc/systemd"
    process3=subprocess.Popen(command3, shell=True, stdout=subprocess.PIPE,stdin=subprocess.PIPE,stderr=subprocess.PIPE)
    stdout3,stderr3=process3.communicate()
    if process3.returncode==0:
        print("\n成功解压并拷贝etc_systemd路径文件\n")
    else:
        print(stderr3)
        print("\n解压并拷贝etc_systemd路径文件失败\n")



    #删除home/zd下的旧config和采集程序
    command4="rm /home/zd/zshy2_app* && rm /home/zd/ConfigData*"
    process4=subprocess.Popen(command4, shell=True, stdout=subprocess.PIPE,stdin=subprocess.PIPE,stderr=subprocess.PIPE)
    stdout4,stderr4=process4.communicate()
    if process4.returncode==0:
        print("成功删除旧zshy2_app和config文件")
    else:
        print(stderr4)
        print("删除旧zshy2_app和config文件失败")

    #写入home/zd目录下的新采集程序等
    print("#######################复制home_zd路径中的文件#######################")
    command5="unzip -o -j 'configuration_files.zip' 'home_zd/*' -d /home/zd"
    #command5="unzip -o -j 'configuration_files.zip' 'home_zd/*' -d /home/zd"
    process5=subprocess.Popen(command5, shell=True, stdout=subprocess.PIPE,stdin=subprocess.PIPE,stderr=subprocess.PIPE)
    stdout5,stderr5=process5.communicate()
    if process5.returncode == 0:
        print("\n成功解压并拷贝home_zd路径文件\n")
    else:
        print(stderr5)
        print("\n解压并拷贝home_zd路径文件失败\n")

    """
    camera_singal=True
    cycle=0
    #先判断USB2.0端口，判断是华星还是sony,再判断有无索尼
    while camera_singal and cycle<2:
        command6="lsusb | grep USB2.0"
        process6=subprocess.Popen(command6, shell=True, stdout=subprocess.PIPE,stdin=subprocess.PIPE,stderr=subprocess.PIPE)
        stdout6=process6.communicate()[0].decode('utf-8')
        if 'USB2.0' in stdout6:
            print("USB2.0存在")
            camera_singal=False
            if 'Sony' in stdout6:
                print("相机是sony\n")
                #此时修改成sony相机的采集程序
                command8=r"mv /home/zd/zshy2_app_Sony* /home/zd/zshy2_app && rm /home/zd/zshy2_app_华星* "
                #command8="mv /home/zd/zshy2_app华星* zshy2_app && rm /home/zd/zshy2_app_Sony* "
                process8 = subprocess.Popen(command8, shell=True, stdout=subprocess.PIPE, stdin=subprocess.PIPE, stderr=subprocess.PIPE)
                print("已经将采集程序修改为sony相机app\n")
            else:
                print("相机是华星\n")
                #修改成华星相机的采集程序
                command9 = r"mv /home/zd/zshy2_app_华星* /home/zd/zshy2_app && rm /home/zd/zshy2_app_Sony*"
                #command9="mv /home/zd/zshy2_app_华星* zshy2_app && rm /home/zd/zshy2_app_Sony*"
                process9 = subprocess.Popen(command9, shell=True, stdout=subprocess.PIPE, stdin=subprocess.PIPE, stderr=subprocess.PIPE)
                print("已经将采集程序修改为华星相机app\n")
        else:
            camera_singal=True
            cycle=cycle+1
            #此时没有USB2.0，说明没有连接相机。再次开启相机通电
            command7 = "echo 1 > /sys/control/power_camera1 && echo 1 > /sys/control/camera_power1"
            process7 = subprocess.Popen(command7, shell=True, stdout=subprocess.PIPE, stdin=subprocess.PIPE, stderr=subprocess.PIPE)
            stdout7 =process7.communicate()
            if cycle==2:
                print("【错误】！！！！！！！没有找到USB2.0端口，请检查相机是否接入！")
    """


def correct_wifi_id():
    #修改hostapd.conf的sid=TK-SMARTEYE-V2-xxxx
    URL = "http://192.168.1.201/pandar.cgi?action=get&object=device_info"
    # data = {
    #     "Body": "你的body值",
#     "SN": "你的序列号"
    # }

    response = requests.get(URL)
    result = response.json()
    # print(json.dumps(result, indent=2))
    SN = result["Body"]["SN"]
    print(f"获取设备雷达实际SN:{SN}\n")
    SN = 'TK' + SN[2:]
    #print(SN)
    WIFI_id =SN[-5:]
    print(WIFI_id)

    #command = "grep -n TK-SMARTEYE /etc/hostapd.conf"
    command1 =f"sed -i 's/.*TK-SMART.*/ssid=TK-SMARTEYE-V2-{WIFI_id}/g' /etc/hostapd.conf"

    process1 = subprocess.Popen(command1, stdout=subprocess.PIPE, stdin=subprocess.PIPE, stderr=subprocess.PIPE,
                               shell=True, text=True)

    #stdout1 = process1.communicate()
    command2 = "grep -n TK-SMARTEYE /etc/hostapd.conf"
    process2=subprocess.Popen(command2, stdout=subprocess.PIPE, stdin=subprocess.PIPE, stderr=subprocess.PIPE, shell=True, text=True)
    stdout2 = process2.communicate()
    print(f"已经修改WIFI_id为:{stdout2[0]}")

    print("#######################修改设备ID#######################")
    device_id = SN

    command3 = f"sed -i 's/\\(DeviceID=\"\\)[^\"]*\"/\\1{device_id}\"/' /home/zd/ConfigData-TkSel.cfg"
    process3 = subprocess.Popen(command3, stdout=subprocess.PIPE, stdin=subprocess.PIPE, stderr=subprocess.PIPE,
                                shell=True, text=True)
    stdout3, stderr3 = process3.communicate()
    if process3.returncode == 0:
        print("修改设备ID成功")
    else:
        print(process3.returncode)
        print(stderr3)
        print("修改设备ID失败，请手动修改！！！")


def Do_Not_Hibernate():
    #运行程序，禁止休眠
    command1="systemctl restart systemd-journald && systemctl stop syslog.socket rsyslog.service && systemctl disable syslog.socket rsyslog.service"
    process1 = subprocess.Popen(command1, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, shell=True)
    process1.communicate()
    time.sleep(2)
    print("写入禁止息屏命令完成")
    command2="systemctl restart systemd-journald && systemctl stop syslog.socket rsyslog.service && systemctl disable syslog.socket rsyslog.service"
    process2 = subprocess.Popen(command2, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, shell=True)
    process2.communicate()
    print("写入禁止休眠命令完成")


def loading_TFcard():
    command1 = "ls /media |grep mmcblk1p1"
    process1 = subprocess.Popen(command1, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, shell=True)
    stdout1 = process1.communicate()
    print(stdout1)
    if "mmcblk1p1" in stdout1[0]:
        print("TF卡已加载")
    else:
        print("【错误】！！！！！！！TF卡未加载，请检查TF卡是否正常！")




def test_speed_of_TFcard():
    print("正在测试TF卡写速度")
    command1="sync;echo 3 > /proc/sys/vm/drop_caches;dd bs=1M count=500 if=/dev/zero of=/media/mmcblk1p1/test.txt"
    try:
        process1 = subprocess.Popen(command1, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, shell=True)
        stdout1 = process1.communicate()
        print(stdout1)
        #print(stderr)
        numbers = re.findall(r'\d+(?:\.\d+)?', stdout1[1][-11:])
        write_speed=float(numbers[0])
        if write_speed >= 15:
            print(f"TF卡写速度正常，为{write_speed}M/s")
        else:
            print(f"【错误】！！！！！！！TF卡写速度过慢{write_speed}，请检查TF卡是否正常！")
    except :
        print("命令失败,请检查TF卡挂载状态")




    print("正在测试TF卡读速度")
    command2="sync;echo 3 > /proc/sys/vm/drop_caches;dd bs=1M count=500 if=/dev/mmcblk1p1 of=/dev/null"
    try:
        process2 = subprocess.Popen(command2, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, shell=True)
        stdout2 = process2.communicate()
        print(stdout2)
        numbers = re.findall(r'\d+(?:\.\d+)?', stdout2[1][-11:])
        read_speed=float(numbers[0])
        if read_speed >= 40:
            print(f"TF卡读速度正常，为{read_speed}M/s")
        else:
            print(f"【错误】！！！！！！！TF卡读速度过慢{read_speed}，请检查TF卡是否正常！")
    except:
        print(f"命令失败,请检查TF卡挂载状态")

def check_camera_function():
    command1="echo 1 > /sys/control/power_camera1 && echo 1 > /sys/control/power_camera1"
    process1 = subprocess.Popen(command1, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, shell=True)
    command2="python3 test_华星视讯.py --mode 16M --device /dev/video0 --output 1.jpg && python3 test_华星视讯.py --mode 16M --device /dev/video2 --output 2.jpg "
    process2=subprocess.Popen(command2, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, shell=True)



if __name__ == '__main__':
    write_configurated_files()
    correct_wifi_id()
    Do_Not_Hibernate()
    #loading_TFcard()
    #test_speed_of_TFcard()