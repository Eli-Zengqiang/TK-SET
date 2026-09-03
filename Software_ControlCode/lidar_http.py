#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2023/11/7 11:25
# @Author  : bhb
# @Email   : 
# @File    : lidar_http.py

import requests


result = requests.get(url="http://192.168.1.201/pandar.cgi?action=get&object=lidar_data&key=lidar_calibration")
print(result.status_code) # 请求状态
print(result.url)# 请求url
print(result.text) # 请求结果