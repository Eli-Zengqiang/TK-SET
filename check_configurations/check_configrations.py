import subprocess
import re
import sys
from sys import stdout, stderr

import requests
import time
from datetime import datetime
import json

def correct_cfg_contents(SN):
    message1,success_signal1,return_message1=check_device_id(SN)
    if success_signal1:
        success_message=return_message1
    else:
        fail_message=return_message1
    success_signal=success_signal1
    print('################正在检查扫描距离配置################\n')
    message =message1 +  '################正在检查扫描距离配置################\n'
    command0 ="sed -i 's/<MaxScanRange>[^<]*<\/MaxScanRange>/<MaxScanRange>30.0000<\/MaxScanRange>/g' /home/zd/ConfigData-TkSel.cfg"
    process0=subprocess.Popen(command0, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, shell=True)
    process0.communicate()
    if process0.returncode == 0:
        print("修改扫描距离为30成功")
        message = message + "修改扫描距离为30成功\n"
        success_message=success_message + "修改扫描距离为30成功\n"
    else:
        print("修改扫描距离失败\n")
        message = message + "修改扫描距离为30失败\n"
        fail_message=fail_message+"修改扫描距离为30失败\n"
        success_signal=False

    print('################正在检查调试模式################\n')
    message = message+'################正在检查调试模式################\n'
    command1="sed -i 's/<MaxScanRange>true<\/MaxScanRange>/<MaxScanRange>false<\/MaxScanRange>/g' /home/zd/ConfigData-TkSel.cfg"
    process1=subprocess.Popen(command1, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, shell=True)
    process1.communicate()


    command2 = "sed -i 's|<OutputTkzTxt>[^<]*</OutputTkzTxt>|<OutputTkzTxt>false</OutputTkzTxt>|g' /home/zd/ConfigData-TkSel.cfg"
    process2=subprocess.Popen(command2,stdout=subprocess.PIPE,stderr=subprocess.PIPE, text=True, shell=True)
    stdout2,stderr2=process2.communicate()
    if process2.returncode==0:
        print("修改调试模式OutputTkzTxt：false成功\n")
        message=message+"修改调试模式成功\n"
        success_message=success_message+"修改调试模式成功\n"

    else:
        print(stderr2)
        print("修改调试模式OutputTkzTxt为false失败\n")

        message=message+"修改调试模式失败\n"
        fail_message = fail_message +"修改调试模式失败\n"
        success_signal = False

    print('################正在检查去噪模式################\n')
    command3 = "sed -i 's|<UseClusterDenoiser>[^<]*</UseClusterDenoiser>|<UseClusterDenoiser>false</UseClusterDenoiser>|g' /home/zd/ConfigData-TkSel.cfg"
    process3=subprocess.Popen(command3,stdout=subprocess.PIPE,stderr=subprocess.PIPE, text=True, shell=True)
    stdout3,stderr3=process3.communicate()
    if process3.returncode==0:
        print("修改除噪点模式：false成功\n")
        message=message+"修改除噪点模式成功\n"
        success_message=success_message+"修改除噪点模式成功\n"
        #success_signal = True
    else:
        print("修改除噪点模式：false失败\n")
        message=message+"修改除噪点模式失败\n"
        success_signal = False
    if success_signal:
        return_message=success_message
    else:
        return_message=fail_message
    return message,success_signal,return_message



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
def Radar_SN():
    print('################获取设备ID###############\n')
    message = '################正在检查wifi配置与cfg中Device-ID################\n'
    URL="http://192.168.1.201/pandar.cgi?action=get&object=device_info"
    # data = {
    #     "Body": "你的body值",
    #     "SN": "你的序列号"
    # }

    response = requests.get(URL)
    result = response.json()
    # print(json.dumps(result, indent=2))
    SN=result["Body"]["SN"]
    print(f"获取雷达SN:{SN}\n")
    SN='TK' + SN[2:]
    print(f"设备ID应为：{SN}")
    return SN


def check_hostapd( SN):#修改wifi名称
    success_signal=True
    success_message=""
    fail_message=""
    message = '################正在检查wifi配置################\n'
    print( '################正在检查wifi配置################\n')
    print("检查hostapd.conf中的ssid\n")
    command = "grep -n TK-SMARTEYE /etc/hostapd.conf"
    process = subprocess.Popen(command, stdout=subprocess.PIPE, stdin=subprocess.PIPE, stderr=subprocess.PIPE,
                               shell=True, text=True)
    stdout = process.communicate()
    ssid = stdout[0][22:-1]
    lenth = len(ssid)
    SN_last = SN[-lenth:]
    WIFI_id = SN[-5:]
    message = message + f"获取wifi配置：{SN_last}\n"

    if ssid == SN_last:
        print(f"ssid-wifi已更新为：{stdout[0][7:]}\n请检查--雷达SN标签纸是否与 {SN} 一致？ \n")
        message = message + f"测试结果：ssid-wifi已更新为：{stdout[0][7:]}\n请检查--雷达SN标签纸是否与 {SN} 一致？ \n"
        #success_signal = True
        success_message = success_message + "ssid-wifi已更新\n"
        # return message
    else:
        command4 = f"sed -i 's/.*TK-SMART.*/ssid=TK-SMARTEYE-V2-{WIFI_id}/g' /etc/hostapd.conf"

        process4 = subprocess.Popen(command4, stdout=subprocess.PIPE, stdin=subprocess.PIPE, stderr=subprocess.PIPE,
                                    shell=True, text=True)

        stdout4, stderr4 = process4.communicate()

        if process4.returncode == 0:
            print(f"已经修改WIFI_id为:{WIFI_id}")
        else:
            print(stderr4)
            print("修改WIFI_id失败，请手动修改！！！\n")
            print(f"ssid-wifi与雷达名称不一致{stdout[0][7:]}，请更新\n并检查--雷达SN标签纸是否与 {SN} 一致？ \n")
            message = message + f"测试结果：ssid-wifi与雷达名称不一致{stdout[0][7:]}，请更新\n并检查--雷达SN标签纸是否与 {SN} 一致？ \n\n\n"
            success_signal = False
            fail_message = fail_message + "ssid-wifi与雷达名称不一致\n"

    if success_signal:
        return_message=success_message
    else:
        return_message=fail_message
    return message,success_signal,return_message


def check_device_id(SN):
    print("################正在检查DeviceID################\n")
    message = "################正在检查DeviceID################\n"
    success_signal=True
    success_message=""
    fail_message=""

    command2 = "grep -n TK /home/zd/ConfigData-TkSel.cfg"
    process2 = subprocess.Popen(command2, stdout=subprocess.PIPE, stdin=subprocess.PIPE, stderr=subprocess.PIPE,
                                shell=True, text=True)
    stdout1 = process2.communicate()
    message = message + f"cfg中DeviceID：{stdout1[0]}\n"
    if SN in stdout1[0]:
        print("cfg中--DeviceID已经更新\n")
        message = message + "测试结果：cfg中--DeviceID已经更新\n"
        success_message = success_message+"cfg中--DeviceID已经更新\n"


    else:
        # print(f"请将cfg中--DeviceID更新为：{SN}\n")
        print(f"{SN}与cfg中{stdout1[0]}不一致\n")
        print("修改设备ID中......\n")
        device_id = SN
        command3 = f"sed -i 's/\\(DeviceID=\"\\)[^\"]*\"/\\1{device_id}\"/' /home/zd/ConfigData-TkSel.cfg"
        process3 = subprocess.Popen(command3, stdout=subprocess.PIPE, stdin=subprocess.PIPE, stderr=subprocess.PIPE,
                                    shell=True, text=True)
        stdout3, stderr3 = process3.communicate()
        if process3.returncode == 0:
            print(f"修改设备ID成功为：{device_id}")
            message = message + "测试结果：cfg中--DeviceID已经更新\n"
            success_message=success_message+"测试结果：cfg中--DeviceID已经更新\n"

        else:
            print(process3.returncode)
            print(stderr3)
            print("修改设备ID失败，请手动修改！！！\n")
            message = message + f"测试结果：请将cfg中--DeviceID更新为：{SN}"
            fail_message =fail_message+ "cfg中--DeviceID未更新\n"
            success_signal = False
    if success_signal:
        return_message=success_message
    else:
        return_message=fail_message
    return message,success_signal,return_message


def check_bftpd():
    print('################正在检查ftp配置################\n')
    success_signal=False
    success_message=""
    fail_message=""

    message = '################正在检查ftp配置################\n'
    #command=["grep", "-n", "DATA_TIMEOUT", "/etc/bftpd.conf"]
    #process = subprocess.Popen(['ls', '-l'], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    command = "grep -n DATA_TIMEOUT /etc/bftpd.conf && grep -n CONTROL_TIMEOUT /etc/bftpd.conf"
    process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True,shell=True)
    stdout, stderr = process.communicate()
    bftpd_out=stdout
    print(f"已有ftp配置：{bftpd_out}")
    message = message + f"已有ftp配置：{bftpd_out}\n"

    if 'DATA_TIMEOUT="10000"' in bftpd_out and 'CONTROL_TIMEOUT="10000"':
        print('bftpd.conf,已经更新\n')
        message = message + f"测试结果：bftpd.conf,已经更新\n"
        success_signal=True
        success_message="bftpd.conf,已经更新\n"

    else:
        print('正在更新bftpd.conf\n')
        message = message + f"正在更新bftpd.conf\n"
        command2 = "sed -i 's/.*DATA_TIMEOUT.*/  DATA_TIMEOUT=\"10000\"/g' /etc/bftpd.conf" \
                   "&& sed -i 's/.*CONTROL_TIMEOUT.*/  CONTROL_TIMEOUT=\"10000\"/g' /etc/bftpd.conf"
        process2 = subprocess.Popen(command2, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, shell=True)
        process2.communicate()
        print("命令返回值:", process2.returncode)
        print('bftpd.conf,已经更新\n')
        message = message + f"测试结果：bftpd.conf,已经更新\n"
        success_signal = True
        success_message = "bftpd.conf,已经更新\n"
    return message,success_signal,success_message


def check_journald():
    print('################正在检查休眠配置################\n')
    #设置取消休眠
    command0 ="systemctl restart systemd-journald && systemctl stop syslog.socket rsyslog.service && systemctl disable syslog.socket rsyslog.service "
    process0 = subprocess.Popen(command0, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, shell=True)
    process0.communicate()
    success_message = ""
    fail_message = ""
    success_signal = False
    message= '################正在检查休眠配置################\n'
    command0 = "grep -n Storage= /etc/systemd/journald.conf " \
              "&&grep -n SystemMaxUse /etc/systemd/journald.conf" \
              "&&grep -n SystemKeepFree /etc/systemd/journald.conf" \
              "&&grep -n MaxRetentionSec /etc/systemd/journald.conf"
    #process = subprocess.Popen(['ls', '-l'], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    process0 = subprocess.Popen(command0, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True,shell=True)
    stdout, stderr = process0.communicate()
    #print(stdout)
    bftpd_out=stdout
    message=f"journald.conf，日志文件为{bftpd_out}"
    print(bftpd_out)
    if 'Storage=persistent' in bftpd_out and 'SystemMaxUse=500M' in bftpd_out and 'SystemKeepFree=50M' in bftpd_out and 'MaxRetentionSec=1month' in bftpd_out:
        print('journald.conf,已经更新 \n')
        message= message + '测试结果：journald.conf,已经更新 \n'
        success_signal = True
        success_message="journald.conf,已经更新 \n'"

    else:
        print('正在更新journald.conf\n')
        message = message + '正在更新journald.conf\n'
        command2 = "sed -i 's/Storage=Auto/Storage=persistent/g' /etc/systemd/journald.conf" \
                   "&& sed -i 's/.*SystemMaxUse.*/SystemMaxUse=500M/g' /etc/systemd/journald.conf " \
                   "&& sed -i 's/.*SystemKeepFree.*/SystemKeepFree=50M/g' /etc/systemd/journald.conf " \
                   "&& sed -i 's/.*MaxRetentionSec.*/MaxRetentionSec=1month/g' /etc/systemd/journald.conf"

        #process = subprocess.Popen(['ls', '-l'], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        process2 = subprocess.Popen(command2, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True,shell=True)
        process2.communicate()
        message = message + '测试结果：journald.conf,已经更新 \n'
        success_signal = True
        success_message = "journald.conf,已经更新 \n"
    print("写入禁止息屏")
    command1="systemctl restart systemd-journald && systemctl stop syslog.socket rsyslog.service && systemctl disable syslog.socket rsyslog.service"
    process1 = subprocess.Popen(command1, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, shell=True)
    process1.communicate()
    time.sleep(5)
    print("写入禁止休眠")
    command2="systemctl restart systemd-journald && systemctl stop syslog.socket rsyslog.service && systemctl disable syslog.socket rsyslog.service"
    process2 = subprocess.Popen(command2, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, shell=True)
    process2.communicate()
    time.sleep(5)
    return message,success_signal,success_message


def camera_id():
    print('################正在检查相机配置################\n')
    message = '################正在检查相机配置################\n'
    sony_cam_signal=0
    success_message = ""
    fail_message = ""
    success_signal = True
    with open('camera_id.txt','w',encoding='utf-8') as file:
        command2 ="sed -n '3,4p' /home/zd/system.json"
        result=subprocess.run(command2, capture_output=True, text=True, shell=True)
        #print("已经进入app/CrSDK/build路径")
        camera_ids=result.stdout
        camera_ids=re.sub(r'\s+', '',camera_ids)
        camera_id1=camera_ids[1:13]
        camera_id2=camera_ids[16:28]
        print("配置文件中的相机id：\n")
        print(camera_id1)
        print(camera_id2)
        message = message + f"相机1_ID：{camera_id1} \n相机2_ID：{camera_id2}\n"

        print("正在检查中，请稍等......")
        message= message + "正在检查中，请稍等......\n"

        command0 = "echo 1 > /sys/control/power_camera1"  # 检查开机时，相机是否已经连接
        process0 = subprocess.Popen(command0, stdout=subprocess.PIPE, stdin=subprocess.PIPE, stderr=subprocess.PIPE,
                                    shell=True, text=True)
        process0.communicate()
        time.sleep(10)


        sony_signal = 'Sony'
        USB2_signal='USB2.0 HUB'
        command2 = "lsusb | grep 'USB2.0 HUB'"  # 检查开机时，相机是否已经连接

        process2 = subprocess.Popen(command2, stdout=subprocess.PIPE, stdin=subprocess.PIPE, stderr=subprocess.PIPE,
                                   shell=True, text=True)
        stdout2 = process2.communicate()[0]

        if  USB2_signal in stdout2 :  # 判断初始相机已经连接
            if sony_signal in stdout2:  #判断为真连接的是sony相机，否则是华星相机
                sony_cam_signal=1
                print("厂商是Sony")
                command3 = "/app/CrSDK/build/RemoteCli"
                #process = subprocess.Popen(['ls', '-l'], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
                process3 = subprocess.Popen(command3, stdout=subprocess.PIPE, stdin=subprocess.PIPE,stderr=subprocess.PIPE,  text=True,shell=True)
                stdout3, stderr3 = process3.communicate(input="\n")
                sony_contents3=stdout3
                print(sony_contents3)
                message= message + f"查询相机有：{sony_contents3}\n"
                if camera_id1 in sony_contents3 or camera_id2 in sony_contents3:
                    print("system.json,已经更新\n")
                    success_message="system.json,已经更新\n"
                    message = message + "测试结果：system.json,已经更新\n"
                elif "No cameras detected" in sony_contents3:
                    print("未检查到相机接入\n")
                    print("请检查相机是否开机，并且 lsusb指令-可以读取到两相机id\n")
                    print("若可读取，请重启相机\n")

                    message = message + "测试结果：未检查到相机接入\n" + "请检查相机是否开机，并且 lsusb指令-可以读取到两相机id\n"
                    success_signal=False
                    fail_message="未检查到相机接入\n"
                else:
                    print("请更新system.json,注意朝前相机id为 '第一个id'：使用拍照，确定相机位置\n")
                    message = message + "测试结果：请更新system.json,注意朝前相机id为 '第一个id'：使用拍照，确定相机位置\n"
                    success_signal = False
                    fail_message="请更新system.json,注意朝前相机id为 '第一个id'：使用拍照，确定相机位置\n"

                file.write(sony_contents3 + '\n')
                file.flush()

            else:

                sony_cam_signal=0
                print("当前相机是华星相机，无需配置相机")
                message = message + "测试结果：当前相机是华星相机，无需配置相机\n"
                success_message = "当前相机是华星相机，无需配置相机\n"




        else:
            print("开机后无法读取到相机，重新上电")
            command4 = "echo 1 > /sys/control/power_camera1 && echo 1 > /sys/control/camera_power1"  # 检查开机时，相机是否已经连接
            process4 = subprocess.Popen(command4, stdout=subprocess.PIPE, stdin=subprocess.PIPE, stderr=subprocess.PIPE,
                                        shell=True, text=True)
            process4.communicate()
            time.sleep(10)

            command5 = "lsusb | grep 'USB2.0 HUB'"  # 检查开机时，相机是否已经连接
            #command5 = "lsusb"  # 检查开机时，相机是否已经连接
            process5 = subprocess.Popen(command5, stdout=subprocess.PIPE, stdin=subprocess.PIPE, stderr=subprocess.PIPE,
                                        shell=True, text=True)
            stdout5 = process5.communicate()[0]
            print(f"第二次自动连接：{stdout5}")
            print(stdout5)
            if  USB2_signal in stdout5:
                #sony_cam_signal=1

                if sony_signal in stdout5:  # 初始相机已经连接
                    sony_cam_signal = 1
                    print("厂商是Sony")
                    command6 = "/app/CrSDK/build/RemoteCli"
                    # process = subprocess.Popen(['ls', '-l'], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
                    process6 = subprocess.Popen(command6, stdout=subprocess.PIPE, stdin=subprocess.PIPE,
                                                stderr=subprocess.PIPE, text=True, shell=True)
                    stdout6, stderr6 = process6.communicate(input="\n")
                    sony_contents6 = stdout6
                    print(f"以下是相机sdk返回数据：\n{sony_contents6}\n")
                    message = message + f"以下是相机sdk返回数据：\n{sony_contents6}\n"
                    if camera_id1 in sony_contents6 or camera_id2 in sony_contents6:
                        print("system.json,已经更新\n")
                        message = message + "测试结果：system.json,已经更新\n"
                        success_message="system.json,已经更新\n"
                        success_signal = True
                    else:
                        success_signal = False
                        fail_message = "system.json,未更新\n"

                else:
                    print("厂商是华星，无需配置相机")
                    sony_cam_signal=0
                    message = message + "测试结果：当前相机是华星相机，无需配置相机\n"
                    success_message = "当前相机是华星相机，无需配置相机\n"

            else:
                print("请检查相机是否开机，并且 lsusb指令-可以读取到两相机id\n")
                message = message + "测试结果：请检查相机是否开机，并且 lsusb指令-可以读取到两相机id\n"
                success_signal = False
                fail_message = "请检查相机是否开机，并且 lsusb指令-可以读取到两相机id\n"

        if success_signal:
            return_message=success_message
        else:
            return_message=fail_message


        return message, success_signal, return_message,sony_cam_signal

def camera_transfer_speed(sony_cam_signal=2):
    print('################正在检查相机降速配置################\n')
    sony_cam_signal=str(sony_cam_signal)
    success_message = ""
    fail_message = ""
    success_signal = False
    if sony_cam_signal == '2':
        cam_vendor = input("sony输入0，华星输入1，不确定请输入 x 退出，并执行检查相机id，确定相机(厂商)类型\n")
    if sony_cam_signal == '1':
        cam_vendor = "0"
        print("厂商是Sony\n")

    elif sony_cam_signal == '0':
        cam_vendor = "1"
        print("厂商是华星相机\n")

    elif cam_vendor=="x":
        file.flush()
        sys.exit()

    message = '################正在检查相机降速配置################\n'
    command = "dmesg | grep 'speed USB'"
    process = subprocess.Popen(command, stdout=subprocess.PIPE, stdin=subprocess.PIPE, stderr=subprocess.PIPE,
                               shell=True, text=True)
    stdout = process.communicate()

    message = message + f"USB连接情况为：\n{stdout}\n"
    print(f"相机输出{stdout[0]}")
    if ('new full-speed' in stdout[0] ) and cam_vendor=="0":
            print(f"USB连接情况：{stdout}")
            print('sony相机usb2.0，已经降速\n')
            message = message + '测试结果：sony相机usb2.0，已经降速\n'
            success_signal=True
            success_message='测试结果：sony相机usb2.0，已经降速\n'

    elif 'new high-speed' in stdout[0] and cam_vendor == "1":
        print(f"USB连接情况：{stdout}")
        print('华星相机速度正常\n')
        message = message + '测试结果：华星相机速度正常\n'
        success_signal = True
        success_message = '测试结果：华星相机速度正常\n'

    else:
        print('相机usb传输速度与厂商不匹配\n')
        message = message + '测试结果：相机usb传输速度与厂商不匹配\n'
        fail_message='相机usb传输速度与厂商不匹配\n'
    if success_signal:
        return_message=success_message
    else:
        return_message = fail_message
    return message,success_signal,return_message


def camera_Fireware():  #使用echo 1 > /sys/control/camera_power1，是否可以开关机，是为新固件
    success_message = ""
    fail_message = ""
    success_signal = False
    print('################正在检查相机固件配置################\n')
    message = '################正在检查相机固件配置################\n'
    sony_signal='Sony'

    command="lsusb | grep 'Sony'"   #检查开机时，相机是否已经连接
    process = subprocess.Popen(command, stdout=subprocess.PIPE, stdin=subprocess.PIPE, stderr=subprocess.PIPE,
                               shell=True, text=True)
    stdout = process.communicate()[0]
    if sony_signal in stdout:  #初始相机已经连接
        print(f"相机已经连接：{stdout}，等待关闭\n")
        message = message + f"相机已经连接：{stdout}，等待关闭"
        command2 = "echo 1 > /sys/control/camera_power1"  #关闭相机，如果成功，固件已更新
        process2 = subprocess.Popen(command2, stdout=subprocess.PIPE, stdin=subprocess.PIPE, stderr=subprocess.PIPE,
                                   shell=True, text=True)
        process2.communicate()
        print("相机关闭中，请等待10s......\n")
        message= message + "相机关闭中，请等待10s......\n"
        time.sleep(10)
        command2 = "lsusb | grep 'Sony'"
        process2 = subprocess.Popen(command2, stdout=subprocess.PIPE, stdin=subprocess.PIPE, stderr=subprocess.PIPE,
                                   shell=True, text=True)
        stdout2 = process2.communicate()
        if sony_signal not in stdout2:
            print(f"相机已经关闭：{stdout2}")
            print("相机固件已更新")
            message = message + "测试结果：相机固件已更新\n"
            success_signal=True
            success_message="相机固件已更新\n"

        else:
            print("请更新相机固件")
            message = message + "测试结果：请更新相机固件\n"
            fail_message="相机固件未更新\n"
            success_signal=False
    else:    #相机未连接，开相机→lsusb查看→关相机→lsusb查看
        command3 = "echo 1 > /sys/control/power_camera1 && echo 1 > /sys/control/camera_power1"  #开相机
        process3 = subprocess.Popen(command3, stdout=subprocess.PIPE, stdin=subprocess.PIPE, stderr=subprocess.PIPE,
                                    shell=True, text=True)
        process3.communicate()
        print("相机开启中，请等待10s......")
        message= message + "相机开启中，请等待10s......\n"
        time.sleep(10)

        command4 = "lsusb | grep 'Sony'"  #查看相机是否开启
        process4 = subprocess.Popen(command4, stdout=subprocess.PIPE, stdin=subprocess.PIPE, stderr=subprocess.PIPE,
                                    shell=True, text=True)
        stdout4 = process4.communicate()[0]

        if sony_signal in stdout4:  # 相机已经连接
            print(f"相机已经连接： {stdout4}")
            message = message + "相机开启中，请等待10s......\n"

            command5 = "echo 1 > /sys/control/camera_power1"  #使用1关相机，如果关闭，则固件已经更新
            process5 = subprocess.Popen(command5, stdout=subprocess.PIPE, stdin=subprocess.PIPE, stderr=subprocess.PIPE,                       shell=True, text=True)
            process5.communicate()
            print(f"相机关闭中，请等待10s......")
            message = message + f"相机关闭中，请等待10s......\n"
            time.sleep(10)

            command6 = "lsusb | grep 'Sony'" #查看相机是否关闭
            process6 = subprocess.Popen(command6, stdout=subprocess.PIPE, stdin=subprocess.PIPE, stderr=subprocess.PIPE,
                                        shell=True, text=True)
            stdout6 = process6.communicate()[0]

            if sony_signal not in stdout6:  #完成关闭
                print(f"相机已经关闭：{stdout6}")
                print("相机固件已更新")
                message = message + "测试结果：相机固件已更新\n"
                success_signal = True
                success_message = "相机固件已更新\n"

            else:
                print("请更新相机固件")
                message = message + "测试结果：请更新相机固件\n"
                success_signal = False
                fail_message = "相机固件未更新\n"


        else:
            print("相机未连接，请检查相机是否开机")
            message = message + "测试结果：相机未连接，请检查相机是否开机\n"
            success_signal = False
            fail_message = "相机固未连接\n"
    if success_signal:
        return_message=success_message
    else:
        return_message = fail_message
    return message,success_signal,return_message

'''
def show_time():  #只有进行联网才行，并且设备连接手机后，自动更新时间,不需要再进行校正
    time=datetime.now()
    surface_time=time.strftime("%Y-%m-%d %H:%M")
    print(surface_time)

    command = "hwclock -r"
    process = subprocess.Popen(command, stdout=subprocess.PIPE, stdin=subprocess.PIPE, stderr=subprocess.PIPE,
                               shell=True, text=True)
    stdout = process.communicate()
    hw_clock=stdout[:15]

    if surface_time == hw_clock:
        print("硬件时间正确")
    else:
        print("正在更新硬件时间")
        now_time=datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(f"当前时间为：{now_time}")
        command = f"date -s '{now_time}';hwclock -w"
        process = subprocess.Popen(command, stdout=subprocess.PIPE, stdin=subprocess.PIPE, stderr=subprocess.PIPE,
                                   shell=True, text=True)
        stdout = process.communicate()
        print(f"写入时间为：{now_time},显示时间为：{stdout}")

'''

if __name__=="__main__":
    kill_app_process()
    test_time=datetime.now()
    test_time=test_time.strftime("%Y-%m-%d %H:%M:%S")
    logs_path=r"/app/check_configuration_results.txt"
    with open(logs_path,'w',encoding='utf-8') as file:
        print(f"\n\n{test_time}:开始检查设备配置\n")
        file.write(f"{test_time}:开始检查设备配置\n")
        file.flush()

        while True:
            print('\n')
            print('\n')
            a=('################################检查设备配置################################\n'
                  '[0]：检查设备所有配置\n'
                  '[1]：检查WIFI名称配置\n'
                  '[2]：检查ftp配置\n'
                  '[3]：检查休眠配置\n'
                  '[4]：检查相机id配置\n'
                  '[5]：检查相机是否降速\n'
                  '[6]：检查相机固件--按钮只是改变当前状态--非sony相机不执行该步骤\n'
                  '[7]：检查cfg文件配置\n'
                  '[x]：退出\n')
            print(a)
            file.write(a)
            file.flush()
            choose_number=input("选择功能：")
            file.write(f"选择功能：{choose_number}\n")
            file.flush()
            if choose_number=="0":
                success_message = ""
                fail_message = ""
                success_numeber=0
                fail_number=0

                print("#####################检查WiFi配置#####################\n")
                file.write("#####################检查WiFi配置#####################\n")
                file.flush()
                SN=Radar_SN()
                message,success_signal,return_message=check_hostapd(SN)
                if success_signal:
                    success_numeber=success_numeber+1
                    success_message=f"{success_numeber}.检查WIFI名称配置成功：WIFI名称已经配置\n"
                else:
                    fail_number=fail_number+1
                    fail_message = f"{fail_number}.检查WIFI名称配置失败"+return_message


                file.write(f"{message}\n")
                file.flush()

                print("#####################检查ftp配置#####################\n")
                file.write("#####################检查ftp配置#####################\n")
                file.flush()
                message, success_signal, return_message =check_bftpd()
                if success_signal:
                    success_numeber=success_numeber+1
                    success_message=success_message+f"{success_numeber}.检查ftp配置成功：ftp已经配置\n"
                else:
                    fail_number=fail_number+1
                    fail_message = fail_message + f"{fail_number}.检查ftp配置失败："+ return_message
                file.write(f"{message}\n")
                file.flush()
                print("#####################检查休眠配置#####################\n")
                file.write("#####################检查休眠配置#####################\n")
                file.flush()
                message, success_signal, return_message=check_journald()
                if success_signal:
                    success_numeber=success_numeber+1
                    success_message=success_message+f"{success_numeber}.检查休眠配置成功：休眠已经配置\n"
                else:
                    fail_number=fail_number+1
                    fail_message = fail_message +f"{fail_number}.检查休眠配置失败："+return_message
                file.write(f"{message}\n")
                file.flush()


                print("#####################检查相机id配置#####################\n")
                file.write("#####################检查相机id配置#####################\n")
                file.flush()
                message, success_signal, return_message,sony_cam_signal = camera_id()

                if success_signal:
                    success_numeber=success_numeber+1
                    success_message=success_message+f"{success_numeber}.检查相机id配置成功：id已经配置\n"
                else:
                    fail_number=fail_number+1
                    fail_message = fail_message +f"{fail_number}.检查相机id配置失败："+return_message
                file.write(f"{message}\n")
                file.flush()

                print("#####################检查相机降速配置#####################\n")
                file.write("#####################检查相机降速配置#####################\n")
                file.flush()
                message, success_signal, return_message = camera_transfer_speed(sony_cam_signal)

                if success_signal:
                    success_numeber=success_numeber+1
                    success_message=success_message+f"{success_numeber}.检查相机降速配置成功：降速配置成功\n"
                else:
                    fail_number=fail_number+1
                    fail_message = fail_message +f"{fail_number}.检查相机降速配置失败："+return_message
                file.write(f"{message}\n")
                file.flush()


                print("#####################检查cfg文件配置#####################\n")
                file.write("#####################检查cfg文件配置#####################\n")
                file.flush()
                message, success_signal, return_message=correct_cfg_contents(SN)
                if success_signal:
                    success_numeber=success_numeber+1
                    success_message=success_message+f"{success_numeber}.cfg文件已配置\n"
                else:
                    fail_number=fail_number+1
                    fail_message = fail_message + f"{fail_number}.cfg文件已配置失败："+return_message

                file.write(f"{message}\n")
                file.flush()

                print(f"\n\n\n完成全部检查\n成功{success_numeber}个：\n{success_message}\n失败{fail_number}个\n{fail_message}\n查看详情，请前往该路径：/app/check_configuration_results.txt\n\n\n")

            elif choose_number=="1":
                print("#####################检查WiFi配置#####################\n")
                file.write("#####################检查WiFi配置#####################\n")
                file.flush()

                SN=Radar_SN()
                message=check_hostapd(SN)
                file.write(f"{message}\n")
                file.flush()

            elif choose_number == "2":
                print("#####################检查ftp配置#####################\n")
                file.write("#####################检查ftp配置#####################\n")
                file.flush()
                message=check_bftpd()
                file.write(f"{message}\n")
                file.flush()

            elif choose_number == "3":
                print("#####################检查休眠配置#####################\n")
                file.write("#####################检查休眠配置#####################\n")
                file.flush()
                message=check_journald()
                file.write(f"{message}\n")
                file.flush()

            elif choose_number == "4":
                print("#####################检查相机id配置#####################\n")
                file.write("#####################检查相机id配置#####################\n")
                file.flush()
                message=camera_id()
                file.write(f"{message}\n")


            elif choose_number == "5":
                print("#####################检查相机降速配置#####################\n")
                file.write("#####################检查相机降速配置#####################\n")
                file.flush()
                message=camera_transfer_speed()
                file.write(f"{message}\n")
                file.flush()


            elif choose_number == "6":
                print("#####################检查相机固件配置#####################\n")
                file.write("#####################检查相机固件配置#####################\n")
                file.flush()
                message=camera_Fireware()
                file.write(f"{message}\n")
                file.flush()

            elif choose_number == "7":
                print("#####################检查cfg文件配置#####################\n")
                file.write("#####################检查cfg文件配置#####################\n")
                file.flush()
                SN=Radar_SN()
                message=correct_cfg_contents(SN)
                file.write(f"{message}\n")
                file.flush()



            elif choose_number == "x":
                print("退出检查")
                message = "退出检查\n"
                file.write(f"{message}\n")
                print("请前往查看检查日志：/app/check_configuration_results.txt")
                file.flush()
                file.close()
                sys.exit()
            else:
                print("请输入0-7之间数字，选择功能项，如果要退出，请输入x")
                message = "请输入0-7之间数字，选择功能项，如果要退出，请输入x"
                file.write(f"{message}\n")
                file.flush()











