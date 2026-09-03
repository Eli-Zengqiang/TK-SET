from CfgClass import CfgClass
from reconstruction import ReconstructionThread
import numpy as np
import shutil
import os
from clac_test import ClacTestThread

def Read_totalstation(file=r"E:\2.1SE-T32\2.1采集数据\20240627棱镜杆\2024-06-27_10-27-35\20240627001.txt"):
    #total_station=[]
    total_stations=[]
    with open(file,'r',encoding='utf-8') as f:
        while True:
            line=f.readline().strip()
            if line:

                total_station=line.split(',')
                total_stations.append(total_station)

            else:
                break
    #print(total_stations)
    return total_stations

sa=CfgClass()
clac_txt_dirs=[r"C:\Users\ZHXR\Desktop\2.1data\tool_or_script\标定工具v1.1_20240522\main\exe\DyCheck\创新大厦2楼平台"]
path=r"E:\2.1SE-T32\2.1采集数据\20240627棱镜杆/"
temp_cfg_path=r"D:\pythonProject\test\pythonProject\smart_eye2_1\2.cfg"
log_file1=r"E:\2.1SE-T32\2.1采集数据\20240627棱镜杆\total_ball.txt"
dir=os.listdir(path)
dirs=[]
#print(dirs)
total_datas=Read_totalstation(file=r"E:\2.1SE-T32\2.1采集数据\20240627棱镜杆\2024-06-27_10-30-20\20240627001.txt")

for i in dir:
    dirs.append(os.path.join(path,i)+r"\\")
print(dirs)

for i,dis in enumerate(dirs):
    original_cfg_path=dis+"ConfigData-TkSel-new.cfg"
    sa.readFromCFG(original_cfg_path)
    length=len(total_datas)
    print(i)
    sa.PrismGeoPoss(total_datas[length-2*(i+1)-2],total_datas[length-2*(i+1)-3])
    print(total_datas[length-2*(i+1)-2],total_datas[length-2*(i+1)-3])
    sa.saveFile(original_cfg_path)
    # rt = ReconstructionThread(dis, temp_cfg_path)
    # rt.run()
    # txt_path = os.path.join(dis, "AllGeoPoints.txt")
    # temp_txt_path = txt_path.replace(".txt", f"{i}.txt")
    # if os.path.isfile(txt_path):
    #     shutil.move(txt_path, temp_txt_path)
    #     clac_t = ClacTestThread(temp_txt_path, clac_txt_dirs[0])  # 比较对应位置的误差
    #     out_strs = clac_t.run()
    #     print(out_strs)

        # print(f"{dis} 已经完成")
        # #TODO：拿到的值怎么来获取最低值？a
        # with open(log_file1,"a+",encoding='utf-8') as f:
        #     for out_str1 in out_strs:
        #         f.write(f"{dis} {out_str1}\n\n")



