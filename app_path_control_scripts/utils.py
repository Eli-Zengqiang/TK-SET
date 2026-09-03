#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2023/8/10 16:15
# @Author  : bhb
# @Email   : 
# @File    : utils.py

'''16进制强转10进制'''
def x2bcd(data):
    out=((data>>4)&0x0f)*10+(data&0x0f)
    return out
