# -*- coding: utf-8 -*-

from prism_ball.CfgClass import CfgClass
from prism_ball.reconstruction import ReconstructionThread
import numpy as np
from prism_ball.read_station_file import read_station_points
from prism_ball.read_folders import read_folders_file
import sys
import paths
import  os
'''
########################设置棱镜球参数###############################
RegGeoMode=['0'] #设置棱镜杆设计值


PrismOffsetAngles=['0']  #设计旋转角
PrismOffsetPos=['0','0','0']  #设计初始位移
#徕卡圆棱镜设计参数
PrismDesignPos_P1=["0.046","-0.7491","-0.1318"]  #设计高棱镜球参数
PrismDesignPos_P0=["0.046","0.7491","-0.1218"]  #设计低棱镜球参数

360棱镜设计参数
PrismDesignPos_P1=["0.046","-0.677","-0.1318"]#设计高棱镜球参数
PrismDesignPos_P0=["0.046","0.677","-0.1218"]#设计低棱镜球参数
'''

def combine_Totalstation_points(datas_folder,total_signal,signal_combine,hand_angles=None):  #combine_Totalstation_points(datas_folder,total_points_file,total_signal):
    log_id=0
    sig=0
    sa = CfgClass()
    #1.先获取当前文件夹下的文件夹名字形成列表 2.根据列表获取cfg，并修改保存 3.合成
    # total_points_file=r"E:\2.1SE-T32\2.1采集数据\20241104詹天佑全站仪测试\全站仪打点\全站仪上采集.txt"   #"E:\2.1SE-T32\2.1采集数据\20241024詹天佑\20241024001副本.txt"
    # datas_folder=r"E:\2.1SE-T32\2.1采集数据\20241106固定件测试/"   #r"E:\2.1SE-T32\2.1采集数据\20241024詹天佑\徕卡圆棱镜1/"

    datas_folders,total_points_file=read_folders_file(datas_folder) #采集数据文件夹子 #datas_folders,total_points_file=read_folders_file(datas_folder)
    # print(f"输出文件路径:{datas_folders}")
    # print(f"全站仪路径:{total_points_file}")
    if total_signal == 2:
        if total_points_file == None:
            print(f"当前合成点云路径中没有全站仪文件,请放入：全站仪打点.txt")
        else:
            prism = read_station_points(total_points_file)
            prism_len=len(prism)

            if prism_len > 2* len(datas_folders):
                TotalStationGeodeticPos_Qiangfeng = prism[2]  # 全站仪的第3行：墙缝打点，棱打点
                print(f"0号楼墙缝坐标为：{TotalStationGeodeticPos_Qiangfeng}")
                sig = 1
                del prism[2]   #删除墙缝打点1
                del prism[2]   #删除墙缝打点2,因为删除了原本第五个元素，第六元素变成了第五个元素
            #print("全站仪坐标行数%s"%(prism_len))
            #print("存在全站仪文件")# 全站仪文件点
                print(prism)
            elif prism_len < 2*len(datas_folders):
                print("请将相机采集的坐标和角度写为0，放入全站仪打点.txt")
                sys.exit(1)


     #temp_cfg_path=r"D:\pythonProject\test\pythonProject\smart_eye2_1\1.cfg"


    log_file1= datas_folder + r"\python循环合成log.txt"


    #dirs=[r"C:\Users\ZHXR\Desktop\2024-07-02_11-09-24/"]
    for dir_id,dir in enumerate(datas_folders):
        datas_folder_len=len(datas_folders)
        if total_signal == 2:

            total_geo = prism[2 * dir_id]  # 全站仪打点
            print(f"全站仪设站：{total_geo}")

            total_angle = prism[2 * dir_id + 1]  # 全站仪旋转角度
            print(f"全站仪角度：{total_angle}")

            original_CFG_path = fr"{dir}/ConfigData-TkSel.cfg"
            print(f"合成cfg路径：{original_CFG_path}")
            original_cfg_path = original_CFG_path
            # 修改cfg，并保存
            sa.readFromCFG(original_cfg_path)
            sa.TotalStationGeodeticPos_cfg(total_geo)  # 修改全站仪设站坐标
            sa.TotalStationRoatationAngle_cfg(total_angle)  # 修改全站仪旋转角度
            # if hand_angles:
            #     sa.TotalStationOffsetAngle_cfg(hand_angles[3])
            #     sa.corret_file_cfg(hand_angles[0],hand_angles[2])
            if sig == 1:
                sa.TotalStationGeodeticPos_Qiangfeng_cfg(TotalStationGeodeticPos_Qiangfeng)
            sa.saveFile(original_cfg_path)

            if signal_combine==2:
                rt = ReconstructionThread(dir,original_cfg_path)  #生成合成点云线程
                rt.run()
            with open(log_file1, 'a+', encoding='utf-8') as f:
                log_id = log_id + 1
                f.write(f"已合成文件夹：{log_id}:{dir} \n")
            print(f"已合成文件个数：{dir_id+1} \n")

            
        elif total_signal == 1:

            original_CFG_path = fr"{dir}/ConfigData-TkSel.cfg"
            original_cfg_path = original_CFG_path
            # 合成点云,如果不需要合成，则注释掉以下3行命令
            rt = ReconstructionThread(dir, original_cfg_path)  #创建点云线程

            print(f"正在合成数据：cfg路径为{original_CFG_path}")
            rt.run()  #运行合成点云线程

            log_id=log_id+1
            with open(log_file1,'a+',encoding='utf-8') as f:
                f.write(f"已合成文件夹：{log_id}:{dir} \n")
        else:
            print("'1'：不考虑设转和旋转角度合成；'2'：全站仪后方交会数据合成；无其他输入参数")
    return datas_folders
if __name__=="__main__":
    #total_points_file=r"F:\2.1SE-T32\2.1采集数据\20250109\1-C555\全站仪打点.txt"  #"E:\2.1SE-T32\2.1采集数据\20241024詹天佑\20241024001副本.txt"
    datas_folder=r"G:\TK-set\2.1data\20260609-4\4B726"   #输入批处理数据文件夹，如果需要后方交会，检查是否有全站仪.txt
    total_signal=2#“2”全站仪后方交会数据；“1”不考虑设站和旋转角度；
    signal_combine=2#当前使用360度合成；2：修改并合成；1：只修改cfg，不合成，#ScanAndProcess-270.exe--270角度合成，ScanAndProcess-360.exe--360角度合成
    combine_Totalstation_points(datas_folder,total_signal,signal_combine)
    print("当前工作目录:", os.getcwd())





