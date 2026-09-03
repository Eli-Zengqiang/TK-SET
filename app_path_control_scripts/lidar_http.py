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
    result = requests.get(url="http://192.168.1.201/pandar.cgi?action=set&object=lidar_data&key=lidar_mode&value=1")
    print(result.text)
    if "Success" in result.text:
        return True
    else:
        return False


print(get_calib())