#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2023/11/7 11:25
# @Author  : bhb
# @Email   : 
# @File    : lidar_http.py

import requests
import json

def get_calib():
    result = requests.get(url="http://192.168.1.201/pandar.cgi?action=get&object=lidar_data&key=lidar_calibration")
    print(result.status_code) # 请求状态
    print(result.url)# 请求url
    need=result.json()['Body']['lidar_calibration']
    print(need) # 请求结果
    return need

def get_info():
    result = requests.get(url="http://192.168.1.201/pandar.cgi?action=get&object=device_info")
    print(result.status_code)  # 请求状态
    print(result.url)  # 请求url
    print(result.text)  # 请求结果

def get_sn():
    result = requests.get(url="http://192.168.1.201/pandar.cgi?action=get&object=device_info")
    print(result.status_code)  # 请求状态
    print(result.url)  # 请求url
    data = result.json()
    sn = data['Body']['SN']
    print(f"设备序列号(SN): {sn}")
    return sn


def get_config():
    result = requests.get(url="http://192.168.1.201/pandar.cgi?action=get&object=lidar_config")
    print(result.status_code)  # 请求状态
    print(result.url)  # 请求url
    print(result.text)  # 请求结果

def set_ptp():#重要
    result = requests.get(url="http://192.168.1.201/pandar.cgi?action=set&object=lidar&key=clock_source&value=1")
    #print(result.status_code)  # 请求状态
    #print(result.url)  # 请求url
    print(result.text)  # 请求结果
    if "Success" in result.text:
        return True
    else:
        return False

def set_return_mode():
    #设置为最强回波
    result = requests.get(url="http://192.168.1.201/pandar.cgi?action=set&object=lidar_data&key=lidar_mode&value=1")
    print(result.text)
    if "Success" in result.text:
        return True
    else:
        return False


#print(get_calib())
#a=[{"i":1,"e":"14.897","a":"-0.000"},{"i":2,"e":"12.871","a":"-0.002"},{"i":3,"e":"10.860","a":"0.000"},{"i":4,"e":"8.861","a":"-0.000"},{"i":5,"e":"6.866","a":"-0.001"},{"i":6,"e":"4.885","a":"-0.007"},{"i":7,"e":"2.904","a":"-0.011"},{"i":8,"e":"0.928","a":"-0.020"},{"i":9,"e":"-1.055","a":"-0.027"},{"i":10,"e":"-3.043","a":"-0.036"},{"i":11,"e":"-5.029","a":"-0.048"},{"i":12,"e":"-7.016","a":"-0.061"},{"i":13,"e":"-9.011","a":"-0.077"},{"i":14,"e":"-11.010","a":"-0.097"},{"i":15,"e":"-13.017","a":"-0.118"},{"i":16,"e":"-15.035","a":"-0.138"}]
