#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2023/8/22 9:15
# @Author  : bhb
# @Email   : 
# @File    : Lidar_XT.py

import socket
import io
import threading
import math
import time
import os

import requests
import json

class Lidar_XT:
    '''
    完全自己写的XT16的类
    :return:
    '''

    def __init__(self):
        self.init_map()
        self.usocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.usocket.bind(("0.0.0.0", 2368))
        self.packets_buffer=[]
        self.lasttime=0.0


    def correct_map(self,correction_content_):
        '''
        根据校准文件更新待查表
        :param str:
        :return:
        '''
        lines=correction_content_.split("\n")
        for i in range(len(lines)-1):
            items=lines[i+1].strip().split(",")
            self.General_elev_angle_map_[i] = float(items[1])
            self.General_horizatal_azimuth_offset_map_[i] = float(items[2])
            self.m_sin_elevation_map_[i] = math.sin(self.General_elev_angle_map_[i] * math.pi / 180)
            self.m_cos_elevation_map_[i] = math.cos(self.General_elev_angle_map_[i] * math.pi / 180)
        self.m_sin_azimuth_map_h=[]
        self.m_cos_azimuth_map_h=[]
        self.m_sin_azimuth_map_b = []
        self.m_cos_azimuth_map_b = []
        for i in range(36000):
            self.m_sin_azimuth_map_h.append(math.sin(i * math.pi / 18000) * 0.0000315)
            self.m_cos_azimuth_map_h.append(math.cos(i * math.pi / 18000) * 0.0000315)
            self.m_sin_azimuth_map_b.append(math.sin(i * math.pi / 18000) * 0.000013)
            self.m_cos_azimuth_map_b.append(math.cos(i * math.pi / 18000) * 0.000013)

    def init_map(self):
        '''
        查表加快速度
        :return:
        '''
        #B1样机的校准参数XXXX
        #lidar_calibration=[{"i":1,"e":"14.975","a":"-0.237"},{"i":2,"e":"12.946","a":"-0.236"},{"i":3,"e":"10.940","a":"-0.229"},{"i":4,"e":"8.947","a":"-0.224"},{"i":5,"e":"6.952","a":"-0.224"},{"i":6,"e":"4.969","a":"-0.227"},{"i":7,"e":"2.987","a":"-0.230"},{"i":8,"e":"1.015","a":"-0.236"},{"i":9,"e":"-0.955","a":"-0.244"},{"i":10,"e":"-2.940","a":"-0.252"},{"i":11,"e":"-4.920","a":"-0.264"},{"i":12,"e":"-6.907","a":"-0.281"},{"i":13,"e":"-8.896","a":"-0.300"},{"i":14,"e":"-10.891","a":"-0.321"},{"i":15,"e":"-12.894","a":"-0.341"},{"i":16,"e":"-14.909","a":"-0.361"}]

        # lidar_calibration=[{"i": 1, "e": "14.959", "a": "-0.094"}, {"i": 2, "e": "12.924", "a": "-0.094"},
        #  {"i": 3, "e": "10.906", "a": "-0.084"}, {"i": 4, "e": "8.899", "a": "-0.080"},
        #  {"i": 5, "e": "6.897", "a": "-0.076"}, {"i": 6, "e": "4.905", "a": "-0.074"},
        #  {"i": 7, "e": "2.915", "a": "-0.075"}, {"i": 8, "e": "0.931", "a": "-0.077"},
        #  {"i": 9, "e": "-1.056", "a": "-0.082"}, {"i": 10, "e": "-3.047", "a": "-0.089"},
        #  {"i": 11, "e": "-5.034", "a": "-0.097"}, {"i": 12, "e": "-7.024", "a": "-0.108"},
        #  {"i": 13, "e": "-9.017", "a": "-0.122"}, {"i": 14, "e": "-11.016", "a": "-0.141"},
        #  {"i": 15, "e": "-13.021", "a": "-0.156"}, {"i": 16, "e": "-15.037", "a": "-0.173"}]#C854
        result = requests.get(url="http://192.168.1.201/pandar.cgi?action=get&object=lidar_data&key=lidar_calibration")
        lidar_calibration = json.loads(result.json()['Body']['lidar_calibration'])
        print(lidar_calibration)  # 拉取数据
        print(type(lidar_calibration))

        correction_content_ = "Laser id,Elevation,Azimuth\n"
        for item in lidar_calibration:
            correction_content_+=f"{item['i']},{item['e']},{item['a']}\n"
        correction_content_=correction_content_[:-2]
        #correction_content_="Laser id,Elevation,Azimuth\n1,14.947,0.521\n2,12.917,0.518\n3,10.907,0.519\n4,8.910,0.515\n5,6.919,0.509\n6,4.938,0.499\n7,2.995,0.491\n" \
         #                   "8,1.079,0.483\n9,-0.904,0.471\n10,-2.894,0.460\n11,-4.887,0.443\n12,-6.881,0.429\n13,-8.877,0.414\n14,-10.877,0.394\n15,-12.884,0.372\n16,-14.901,0.347"

        


        self.pandarXT_elev_angle_map = [15.0, 14.0, 13.0, 12.0, 11.0, 10.0, 9.0, 8.0, 7.0, 6.0, 5.0, 4.0, 3.0, 2.0, 1.0,
                                        0.0, -1.0, -2.0, -3.0, -4.0, -5.0, -6.0, -7.0, -8.0, -9.0, -10.0, -11.0, -12.0,
                                        -13.0, -14.0, -15.0, -16.0]

        self.blockXTOffsetDual_ = [
            5.632 - 50.0 * 3.0,
            5.632 - 50.0 * 3.0,
            5.632 - 50.0 * 2.0,
            5.632 - 50.0 * 2.0,
            5.632 - 50.0 * 1.0,
            5.632 - 50.0 * 1.0,
            5.632 - 50.0 * 0.0,
            5.632 - 50.0 * 0.0]

        self.blockXTOffsetSingle_ = [
            5.632 - 50.0 * 7.0,
            5.632 - 50.0 * 6.0,
            5.632 - 50.0 * 5.0,
            5.632 - 50.0 * 4.0,
            5.632 - 50.0 * 3.0,
            5.632 - 50.0 * 2.0,
            5.632 - 50.0 * 1.0,
            5.632 - 50.0 * 0.0
        ]

        self.blockXTOffsetDual_=[
            5.632 - 50.0 * 2.0,
    5.632 - 50.0 * 2.0,
    5.632 - 50.0 * 1.0,
    5.632 - 50.0 * 1.0,
    5.632 - 50.0 * 0.0,
    5.632 - 50.0 * 0.0,
    5.632 - 50.0 * 0.0,
    5.632 - 50.0 * 0.0]

        laserXTOffset = [
            1.512 * 0.0 + 0.368,
            1.512 * 1.0 + 0.368,
            1.512 * 2.0 + 0.368,
            1.512 * 3.0 + 0.368,
            1.512 * 4.0 + 0.368,
            1.512 * 5.0 + 0.368,
            1.512 * 6.0 + 0.368,
            1.512 * 7.0 + 0.368,

            1.512 * 8.0 + 0.368,
            1.512 * 9.0 + 0.368,
            1.512 * 10.0 + 0.368,
            1.512 * 11.0 + 0.368,
            1.512 * 12.0 + 0.368,
            1.512 * 13.0 + 0.368,
            1.512 * 14.0 + 0.368,
            1.512 * 15.0 + 0.368,

            1.512 * 16.0 + 0.368,
            1.512 * 17.0 + 0.368,
            1.512 * 18.0 + 0.368,
            1.512 * 19.0 + 0.368,
            1.512 * 20.0 + 0.368,
            1.512 * 21.0 + 0.368,
            1.512 * 22.0 + 0.368,
            1.512 * 23.0 + 0.368,

            1.512 * 24.0 + 0.368,
            1.512 * 25.0 + 0.368,
            1.512 * 26.0 + 0.368,
            1.512 * 27.0 + 0.368,
            1.512 * 28.0 + 0.368,
            1.512 * 29.0 + 0.368,
            1.512 * 30.0 + 0.368,
            1.512 * 31.0 + 0.368]

        self.m_sin_elevation_map_ = []
        self.m_cos_elevation_map_ = []
        self.General_elev_angle_map_ = []
        self.General_horizatal_azimuth_offset_map_ = []
        self.laserXTOffset_ = []
        for i in range(16):
            self.m_sin_elevation_map_.append(math.sin(self.pandarXT_elev_angle_map[i * 2] * math.pi / 180))
            self.m_cos_elevation_map_.append(math.cos(self.pandarXT_elev_angle_map[i * 2] * math.pi / 180))
            self.General_elev_angle_map_.append(self.pandarXT_elev_angle_map[i * 2])
            self.General_horizatal_azimuth_offset_map_.append(0.0)
            self.laserXTOffset_.append(laserXTOffset[i * 2])
        self.correct_map(correction_content_)
        self.m_sin_azimuth_map_=[]
        self.m_cos_azimuth_map_=[]
        for i in range(36000):
            self.m_sin_azimuth_map_.append(math.sin(i * math.pi / 18000))
            self.m_cos_azimuth_map_.append(math.cos(i * math.pi / 18000))


    def start_read(self):
        self.packets_buffer.clear()
        self.is_recv_thread_running = True

        self.recv_thread = threading.Thread(target=self.recv_data)
        self.recv_thread.start()

    def stop_read(self):

        self.is_recv_thread_running = False

    def start_write(self,filename="t1.txt"):
        self.is_write_thread_running = True
        self.write_thread = threading.Thread(target=self.write_to_file,args=(filename,))
        self.write_thread.start()

    def stop_write(self):
        self.is_write_thread_running = False
        while self.write_thread.is_alive():
            time.sleep(1)


    def recv_data(self):
        while self.is_recv_thread_running:
            try:
                data = self.usocket.recv(1500)
                if len(data) == 568:
                    self.packets_buffer.append(data)
            except Exception as e:
                print(e)
                break

    def prash_data(self, recvbuf,need_add_8=False):
        '''
        解析xt16数据
        :param data:
        :return:
        '''

        packet = {}
        header = {}
        header['sob'] = (recvbuf[0] & 0xff) << 8 | ((recvbuf[1] & 0xff))
        if header['sob'] != 0xEEFF:
            print("Error Start of Packet!\n")
            return
        header['chProtocolMajor'] = recvbuf[2] & 0xff
        header['chProtocolMinor'] = recvbuf[3] & 0xff
        header['chLaserNumber'] = recvbuf[6] & 0xff
        header['chBlockNumber'] = recvbuf[7] & 0xff
        header['chReturnType'] = recvbuf[8] & 0xff
        header['chDisUnit'] = recvbuf[9] & 0xff

        packet["header"] = header
        packet["echo"] = recvbuf[550] & 0xff

        year = (recvbuf[553] & 0xff)  +2000# 553
        if year>=2100:
            year-=100
        month = (recvbuf[554] & 0xff)
        day = recvbuf[555] & 0xff
        hour = recvbuf[556] & 0xff
        minute = recvbuf[557] & 0xff
        second = recvbuf[558] & 0xff
        timeArray = time.strptime(f"{year}-{month}-{day} {hour}:{minute}:{second}", "%Y-%m-%d %H:%M:%S")
        unix_second = time.mktime(timeArray)
        timestamp = (recvbuf[559] & 0xff) | (recvbuf[560] & 0xff) << 8 | (
                (recvbuf[561] & 0xff) << 16) | ((recvbuf[562] & 0xff) << 24)
        point_timestamp=unix_second+timestamp/1000000.0
        packet["timestamp"]=point_timestamp

        index=12
        packet["points"] = []
        for block in range(header['chBlockNumber']):
            block_azimuth = (recvbuf[index] & 0xff) | ((recvbuf[index + 1] & 0xff) << 8)
            index += 2
            for i in range (header['chLaserNumber']):
                azimuth = int(self.General_horizatal_azimuth_offset_map_[i] * 100 + block_azimuth)
                if azimuth < 0:
                    azimuth += 36000
                if azimuth > 36000:
                    azimuth -= 36000
                unRange = (recvbuf[index] & 0xff) | ((recvbuf[index + 1] & 0xff) << 8)
                unit_distance=unRange*header['chDisUnit'] / 1000.0
                # if unit_distance <= 0.1 or unit_distance > 200.0:
                #     continue
                distance=unit_distance - (self.m_cos_azimuth_map_h[abs(int(self.General_horizatal_azimuth_offset_map_[i] * 100))] * self.m_cos_elevation_map_[i] -
                                         self.m_sin_azimuth_map_b[abs(int(self.General_horizatal_azimuth_offset_map_[i] * 100))] * self.m_cos_elevation_map_[i])
                xyDistance=distance* self.m_cos_elevation_map_[i]
                x = xyDistance * self.m_sin_azimuth_map_[azimuth]- self.m_cos_azimuth_map_b[azimuth] + self.m_sin_azimuth_map_h[azimuth]#
                y = xyDistance * self.m_cos_azimuth_map_[azimuth]+ self.m_sin_azimuth_map_b[azimuth] + self.m_cos_azimuth_map_h[azimuth]#
                z = distance * self.m_sin_elevation_map_[i]#
                intensity = (recvbuf[index + 2] & 0xff)
                confidence=(recvbuf[index + 3] & 0xff)
                if packet["echo"] == 0x39 or packet["echo"] == 0x3b or packet["echo"] == 0x3c:
                    _timestamp = point_timestamp + (self.blockXTOffsetDual_[block] + self.laserXTOffset_[i])/1000000.0#-1561400000
                else:
                    _timestamp = point_timestamp + (
                                self.blockXTOffsetSingle_[block] + self.laserXTOffset_[i]) / 1000000.0  # -1561400000

                if need_add_8:
                    _timestamp+=8*60*60
                self.lasttime=_timestamp
                point_str=f"{x} {y} {z} {intensity} {confidence} {i} {_timestamp}\n"
                packet["points"].append(point_str)
                index += 4
        return packet



    def write_to_file(self,filename):
        print("buffer_num:", len(self.packets_buffer))
        with io.open(filename,"wb") as f:
            while self.is_write_thread_running or len(self.packets_buffer)>0:
                buffer_num=len(self.packets_buffer)
                if buffer_num>0:
                    f.write(self.packets_buffer[0])
                    del self.packets_buffer[0]


    def read_lidar_bin(self,path=r"E:\Code\GitSource\linuxCameraPad201\t1.txt",out_path=r"E:\Code\GitSource\linuxCameraPad201\t2.txt",need_add_8=True):
        '''

        :param path:
        :return:
        '''
        _lines=[]
        with open(path,"rb") as f:
            filesize = os.stat(path).st_size
            print(filesize)
            curren_size=0
            while curren_size<filesize:
                data=f.read(568)
                _str=self.prash_data(data,need_add_8)
                _lines.extend(_str["points"])
                curren_size+=568
        with open(out_path,"w") as f:
            f.writelines(_lines)

    def free_xt(self):
        '''
        关闭socket,清空内存
        :return:
        '''
        self.usocket.close()
        self.packets_buffer.clear()



import sys
if __name__ == "__main__":
    file_name="test.txt"
    during_time=3
    if len(sys.argv)>1:#脚本后面带文件名
        file_name=sys.argv[1]
        if len(sys.argv) > 2:  # 脚本后面带文件名
            during_time = int(sys.argv[2])

    xt = Lidar_XT()
    print("开始收集的时间：", time.time())
    xt.start_read()
    time.sleep(during_time)#需要雷达采集的时间
    xt.stop_read()
    print("停止收集的时间：", time.time())
    xt.start_write(file_name)
    xt.stop_write()
    print("停止写入的时间：", time.time())
    print("解析数据")
    xt.read_lidar_bin(file_name,file_name+".txt")
