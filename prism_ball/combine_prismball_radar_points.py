# -*- coding: utf-8 -*-

from CfgClass import CfgClass
from reconstruction import ReconstructionThread
import numpy as np
from read_station_file import read_station_points
from read_folders import read_folders_file
########################设置棱镜球参数###############################
RegGeoMode=['0'] #设置棱镜杆设计值


PrismOffsetAngles=['0']  #设计旋转角
PrismOffsetPos=['0','0','0']  #设计初始位移
#徕卡圆棱镜设计参数
PrismDesignPos_P1=["0.046","-0.7491","-0.1218"]  #设计高棱镜球参数
PrismDesignPos_P0=["0.046","0.7491","-0.1318"]  #设计低棱镜球参数

# #360棱镜设计参数
# PrismDesignPos_P1=["0.046","-0.677","-0.1218"]#设计高棱镜球参数
# PrismDesignPos_P0=["0.046","0.677","-0.1318"]#设计低棱镜球参数
log_id=0
sa = CfgClass()


#1.先获取当前文件夹下的文件夹名字形成列表 2.根据列表获取cfg，并修改保存 3.合成
total_points_file=r"E:\2.1SE-T32\2.1采集数据\20241112验证10-20m\全站仪打点\全站仪打点.txt"   #"E:\2.1SE-T32\2.1采集数据\20241024詹天佑\20241024001副本.txt"
get_datas_folder=r"E:\2.1SE-T32\2.1采集数据\20241112验证10-20m\全站仪数据采集/"   #r"E:\2.1SE-T32\2.1采集数据\20241024詹天佑\徕卡圆棱镜1/"
prism=read_station_points(total_points_file)  #全站仪点文件
get_datas_folders=read_folders_file(get_datas_folder) #采集数据文件夹子

#temp_cfg_path=r"D:\pythonProject\test\pythonProject\smart_eye2_1\1.cfg"
log_file1=r"C:\Users\ZHXR\Desktop\2.1data\2.1cloud_combine_tool\合成-0516\python循环合成log.txt"


#dirs=[r"C:\Users\ZHXR\Desktop\2024-07-02_11-09-24/"]
for dir_id,dir in enumerate(get_datas_folders):
    # total_geo=prism[2*dir_id]  #全站仪打点
    # total_angle=prism[2 * dir_id+1]  #全站仪旋转角度
    prism1 = prism[2*dir_id]  #上棱镜球坐标
    prism0= prism[2 * dir_id+1] #下棱镜球坐标
    # if dir_id > 0:
    #     break
    original_CFG_path = fr"{dir}/ConfigData-TkSel.cfg"
    print(f"合成cfg路径：{original_CFG_path}")
    original_cfg_path = original_CFG_path

    sa.readFromCFG(original_cfg_path)
    # sa.TotalStationGeodeticPos_cfg(total_geo)     #修改全站仪设站坐标
    # sa.TotalStationRoatationAngle_cfg(total_angle)  #修改全站仪旋转角度

    sa.RegGeoMode_cfg(RegGeoMode)
    sa.PrismOffsetPos_cfg(PrismOffsetPos)     #修改棱镜杆平移位置
    sa.PrismOffsetAngle_cfg(PrismOffsetAngles)   #修改棱镜杆旋转角度
    sa.PrismDesignPos_P1_cfg(PrismDesignPos_P0,PrismDesignPos_P1)  #写入棱镜球设计参数
    sa.corret_prismball_file_cfg(prism0,prism1)   #写入棱镜球的坐标
    sa.saveFile(original_cfg_path)
    #rt = ReconstructionThread(dir, temp_cfg_path)
    rt = ReconstructionThread(dir,original_cfg_path)
    rt.run()
    log_id=log_id+1
    with open(log_file1,'a+',encoding='utf-8') as f:
        f.write(f"已合成文件夹：{log_id}:{dir} \n")




