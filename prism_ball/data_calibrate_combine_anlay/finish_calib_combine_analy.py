# -*- coding: utf-8 -*-
from pathlib import Path
import combine_run_bat_calibrate
from combine_station_radar_points import combine_Totalstation_points
from 联合精度测试 import cacl_error
import CfgClass
from crop_pointcloud import crop_pointscloude
from pointcloud_layer_analyze import analyze_pointcloud
from  single_device_test_distance_errorbar import draw_distance_errorbar

if __name__=="__main__":
    data_paths =[ r"G:\TK-set\2.1data\20260807\b524\2026-08-07_10-45-44/" ]##需要标定的数据文件夹要加"/"
    for data_path in data_paths:
        upper_path= Path(data_path)
        # 需要合成的数据文件夹data_path的上级目录
        datas_folder=str(upper_path.parent)+'/'
        print(f"父级目录为：{datas_folder}")

        #TODO###################进行角度写入###################
        #total_points_file=r"F:\2.1SE-T32\2.1采集数据\20250109\1-C555\全站仪打点.txt"  #"E:\2.1SE-T32\2.1采集数据\20241024詹天佑\20241024001副本.txt"
        #需要合成的数据文件夹
        #datas_folder=r"G:\TK-set\2.1data\20260526-4\5B121-0"   #输入批处理数据文件夹，如果需要后方交会，检查是否有全站仪.txt
        total_signal=2#“2”全站仪后方交会数据；“1”不考虑设站和旋转角度；
        signal_combine=1#当前使用360度合成；2：修改并合成；1：只修改cfg，不合成，#ScanAndProcess-270.exe--270角度合成，ScanAndProcess-360.exe--360角度合成
        combine_Totalstation_points(datas_folder,total_signal,signal_combine) #墙缝的点是第三个第四个点。也就是2 3

        #TODO###################进行数据标定###################
        #需要标定的数据文件路径
        #data_path=r"G:\TK-set\2.1data\20260526-4\5B121-0\2026-05-20_15-25-02/"
        #TODO斌哥标定脚本的路径,通常路径不会改变
        bat_path =  r"C:\Users\ZHXR\Desktop\com_tool\2.1data\2.1cloud_combine_tool\标定-0516\180标定-0.5\智隧慧眼2.1标定.bat"
        hand_angles=None
        #XXX
        #标定雷达角度、把手角度，并返回值
        hand_angles=combine_run_bat_calibrate.run_bat_to_calibrate(bat_path,data_path)
        #cfg路径
        cfg_path=data_path+"ConfigData-TkSel.cfg"
        sa=CfgClass()
        #打开cfg
        sa.readFromCFG(cfg_path)
        #写入雷达安装角度
        sa.corret_file_cfg(hand_angles[0],hand_angles[2])
        #写入站仪把手角度
        sa.TotalStationOffsetAngle_cfg(hand_angles[3])
        #保存cfg
        sa.saveFile(cfg_path)


        #TODO###################进行数据合成###################
        #datas_folder = r"G:\TK-set\2.1data\20260526-4\5B121-0"
        total_signal = 2
        signal_combine = 2
        if hand_angles:
            hand_angles=hand_angles
        else:
            hand_angles=None

        datas_folders=combine_Totalstation_points(datas_folder, total_signal, signal_combine,hand_angles)#,hand_angles=None
        #combine_Totalstation_points(datas_folder, total_signal, signal_combine)  # ,hand_angles=None
        #datas_folders=[r"G:\TK-set\2.1data\20260526-4\5B121-0\2026-05-20_14-32-37",r"G:\TK-set\2.1data\20260526-4\5B121-0\2026-05-20_15-25-02",r"G:\TK-set\2.1data\20260526-4\5B121-0\2026-05-20_16-19-37",r"G:\TK-set\2.1data\20260526-4\5B121-0\2026-05-26_16-55-41"]

        # # TODO###################进行精度计算###################
        print(datas_folders)
        cacl_error(datas_folders)

        # TODO###################绘制误差棒图###################

        draw_distance_errorbar(datas_folders)

        # TODO###################进行点云截取###################
        #in_path = r"G:\TK-set\2.1data\20260526-4\8C25F点云分层1.67cm\2026-05-26_17-02-19\AllGeoPoints.txt"
        #out_path = r"G:\TK-set\2.1data\20260526-4\8C25F点云分层1.67cm\2026-05-26_17-02-19\crop_AllGeoPoints.txt"
        in_path = datas_folders[3]
         #截取点云存放位置
        crop_pointscloude(in_path)

        # TODO###################识别点云分层###################
        analyze_pointcloud(in_path)