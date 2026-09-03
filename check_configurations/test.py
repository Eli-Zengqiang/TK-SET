import subprocess
import requests
import time
import re
import os
camera_singal=True
  cycle=0
  #先判断USB2.0端口，判断是华星还是sony,再判断有无索尼
  while camera_singal and cycle<2:
      command6="lsusb | grep USB2.0"
      process6=subprocess.Popen(command6, shell=True, stdout=subprocess.PIPE,stdin=subprocess.PIPE,stderr=subprocess.PIPE)
      stdout6=process6.communicate()[0]
      if 'USB2.0' in stdout5:
          print("USB2.0存在")
          camera_singal=False
          if 'Sony' in stdout6:
              print("相机是sony")
              #此时修改成sony相机的采集程序
              command8=r"mv /app/acc/zshy2_app_Sony* /app/acc/zshy2_app && rm /app/acc/zshy2_app华星* "
              #command8="mv /home/zd/zshy2_app华星* zshy2_app && rm /home/zd/zshy2_app_Sony* "
              process8 = subprocess.Popen(command8, shell=True, stdout=subprocess.PIPE, stdin=subprocess.PIPE, stderr=subprocess.PIPE)

          else:
              print("相机是华星")
              #修改成华星相机的采集程序
              command9 = r"mv /app/acc/zshy2_app_华星* /app/acc/zshy2_app && rm app/acc/zshy2_app_Sony*"
              #command9="mv /home/zd/zshy2_app_华星* zshy2_app && rm /home/zd/zshy2_app_Sony*"
              process9 = subprocess.Popen(command9, shell=True, stdout=subprocess.PIPE, stdin=subprocess.PIPE, stderr=subprocess.PIPE)
      else:
          camera_singal=True
          cycle=cycle+1
          #此时没有USB2.0，说明没有连接相机。再次开启相机通电
          command7 = "echo 1 > /sys/control/power_camera1 && echo 1 > /sys/control/camera_power1"
          process7 = subprocess.Popen(command7, shell=True, stdout=subprocess.PIPE, stdin=subprocess.PIPE, stderr=subprocess.PIPE)
          stdout7 =process7.communicate()
          if cycle==2:
              print("【错误】！！！！！！！没有找到USB2.0端口，请检查USB2.0端口是否正常！")