# -*- coding: utf-8 -*-

from CfgClass import CfgClass
from reconstruction import ReconstructionThread
import numpy as np
import shutil
import os
from clac_test import ClacTestThread


# inc_x_add_start=0.5
# inc_x_add_end=0.5
# inc_y_add_start=0.5
# inc_y_add_end=0.5
# inc_setp=0.01


# ladar_x_add_start=-0.15
# ladar_x_add_end=0.05
# ladar_z_add_start=20.17
# ladar_z_add_end=20.37
# ladar_x_setp=0.01
# ladar_z_setp=0.01

ladar_x_add_start=-0.15
ladar_x_add_end=-0.14
ladar_z_add_start=20.17
ladar_z_add_end=20.18
ladar_x_setp=0.01
ladar_z_setp=0.01

sa = CfgClass()
original_cfg_path1=r"E:\2.1SE-T32\2.1采集数据\20250528-CF52雷达倾角仪测试\20240528-CF52radar测试雷达倾角仪\2024-05-27_16-28-52-0楼\ConfigData-TkSel-new270.cfg"
original_cfg_path2=r"E:\2.1SE-T32\2.1采集数据\20250528-CF52雷达倾角仪测试\20240528-CF52radar测试雷达倾角仪\2024-05-27_15-40-43-1楼\ConfigData-TkSel-new270.cfg"
original_cfg_path3=r"E:\2.1SE-T32\2.1采集数据\20250528-CF52雷达倾角仪测试\20240528-CF52radar测试雷达倾角仪\2024-05-27_17-58-11-2楼平台\ConfigData-TkSel-new270.cfg"

temp_cfg_path=r"D:\pythonProject\test\pythonProject\smart_eye2_1\2.cfg"
dirs=[r"E:\2.1SE-T32\2.1采集数据\20250528-CF52雷达倾角仪测试\20240528-CF52radar测试雷达倾角仪\2024-05-27_16-28-52-0楼/",r"E:\2.1SE-T32\2.1采集数据\20250528-CF52雷达倾角仪测试\20240528-CF52radar测试雷达倾角仪\2024-05-27_15-40-43-1楼/",r"E:\2.1SE-T32\2.1采集数据\20250528-CF52雷达倾角仪测试\20240528-CF52radar测试雷达倾角仪\2024-05-27_17-58-11-2楼平台/"]
#dirs需要与clac_txt_dirs一一对应
clac_txt_dirs=[r"C:\Users\ZHXR\Desktop\2.1data\tool_or_script\标定工具v1.1_20240522\main\exe\DyCheck\0号楼",
               r"C:\Users\ZHXR\Desktop\2.1data\tool_or_script\标定工具v1.1_20240522\main\exe\DyCheck\1楼",
               r"C:\Users\ZHXR\Desktop\2.1data\tool_or_script\标定工具v1.1_20240522\main\exe\DyCheck\创新大厦2楼平台"]


log_file1=r"E:\2.1SE-T32\2.1采集数据\20250528-CF52雷达倾角仪测试\20240528-CF52radar测试雷达倾角仪\2024-05-27_16-28-52-0楼\log1.txt"
log_file2=r"E:\2.1SE-T32\2.1采集数据\20250528-CF52雷达倾角仪测试\20240528-CF52radar测试雷达倾角仪\2024-05-27_16-28-52-0楼\log2.txt"
for dir_id,dir in enumerate(dirs):
    x_range = np.arange(ladar_x_add_start, ladar_x_add_end, ladar_x_setp)
    z_range = np.arange(ladar_z_add_start, ladar_z_add_end, ladar_z_setp)
    if dir_id == 0:
        original_cfg_path=original_cfg_path1
        location="0号楼"
    elif dir_id == 1:

        original_cfg_path = original_cfg_path2
        location = "1楼"
        print("跳过1楼")

    else:
        break
        original_cfg_path = original_cfg_path3
        location = "2楼平台"
        print("跳过2楼")



    #TODO:  增加变量记录最优解
    for x in x_range:
        results = []
        res_list_2 = []
        for z in z_range:
            result = [None] * 5
            print(f"当前角度设置：x={x},z={z}")
            sa.readFromCFG(original_cfg_path)
            sa.corret_file_cfg(x,z)
            sa.saveFile(temp_cfg_path)
            rt=ReconstructionThread(dir,temp_cfg_path)
            rt.run()
            txt_path=os.path.join(dir,"AllGeoPoints.txt")
            temp_txt_path=txt_path.replace(".txt",f"_ladar_{round(x,3)}_{round(z,3)}.txt")
            if os.path.isfile(txt_path):
                shutil.move(txt_path,temp_txt_path)
                clac_t=ClacTestThread(temp_txt_path,clac_txt_dirs[dir_id])#比较对应位置的误差
                a,out_strs=clac_t.run()
                #a = np.array(out_strs)

                path=dir+f"{location}radar{round(x,3)}_{round(z,3)}.npy"
                np.save(path, a)
                print(dir+f"{location}radar{round(x,3)}_{round(z,3)}.npy"+'已完成')
        #         print(np.abs(a).mean(), np.abs(a).max(), a.std())
        #         print(out_strs)
        #         result[0]=location
        #         result[1]=f"{x}-{z}"
        #         result[2]=np.abs(a).mean()
        #         result[3] = np.abs(a).max()
        #         result[4] =  a.std()
        #         results.append(result)
        #         #print(2)
        #
        #
        #         print(f"{results}+'\n'")
        #         #TODO：拿到的值怎么来获取最低值？a
        #         with open(log_file1,"a+",encoding='utf-8') as f:
        #             for out_str in out_strs:
        #                 f.write(f"{x}_{z} {out_str}\n")
        #             f.write(f"lidar{x}_{z}整体误差:平均误差：{np.abs(a).mean()}，最大误差：{np.abs(a).max()},标准误差：{ a.std()}\n\n")
        #
        # for res_list in results:
        #     res_list_2.append(res_list[4])
        # if res_list_2:
        #     min_value=min(res_list_2)
        #     min_index=res_list_2.index(min_value)
        #     for i,res_list in enumerate(results):
        #         if res_list[4]==min_value:
        #             print(f"最小标准误差数据：{results[i]}")
        #
        #             with open(log_file2, "a+",encoding='utf-8') as f:
        #                 f.write(str(results[i])+"\n\n")
        #
        #         else:
        #             print("查询失败")





