# -*- coding: utf-8 -*-

from CfgClass import CfgClass
from reconstruction import ReconstructionThread
import numpy as np
import shutil
import os
#from correct_tk import correct_TK
from clac_test import ClacTestThread
sa = CfgClass()

#0.0189
start_handle_angle=93  #91.20
end_handle_angle=94
step=0.2


#inc_range=np.array(start_inc,end_inc,step)
original_CFG_path1=r"F:\2.1SE-T32\2.1data\20250515CB55-CC53-C854\8CC53\2025-05-15_16-11-17-01\ConfigData-TkSel.cfg"
original_CFG_path2=r"E:\2.1SE-T32\2.1data\CE56\2024-06-24_10-16-35-1楼瓷砖\ConfigData-TkSel-new.cfg"
original_CFG_path3=r"E:\2.1SE-T32\2.1data\CE56\2024-06-24_11-15-18-2楼瓷砖\ConfigData-TkSel-new.cfg"

temp_cfg_path=r"D:\pythonProject\test\pythonProject\smart_eye2_1\1.cfg"
# dirs=[r"F:\2.1SE-T32\2.1data\20250311-c854\2025-03-11_10-54-10副本/",
#     r"F:\2.1SE-T32\2.1data\20250311-c854\2025-03-11_10-54-10副本/",
#     r"F:\2.1SE-T32\2.1data\20250311-c854\2025-03-11_10-54-10副本/"]
#dirs需要与clac_txt_dirs一一对应
dirs=[r"F:\2.1SE-T32\2.1data\20250515CB55-CC53-C854\8CC53\2025-05-15_16-11-17-01"]
clac_txt_dirs=[r"C:\Users\ZHXR\Desktop\2.1data\tool_or_script\标定工具v1.1_20240522\main\exe\DyCheck\0号楼",
               r"C:\Users\ZHXR\Desktop\2.1data\tool_or_script\标定工具v1.1_20240522\main\exe\DyCheck\1楼",
               r"C:\Users\ZHXR\Desktop\2.1data\tool_or_script\标定工具v1.1_20240522\main\exe\DyCheck\创新大厦2楼平台"]
log_file1=fr"{dirs[0]}_total_hands.txt"
# log_file2=r"E:\2.1SE-T32\2.1采集数据\CE56\2024-06-24_10-16-35-1楼瓷砖\total_hands.txt"
# log_file3=r"E:\2.1SE-T32\2.1采集数据\CE56\2024-06-24_11-15-18-2楼瓷砖\total_hands.txt"
#log_file2=r"E:\2.1SE-T32\2.1采集数据\CE56\best_std_inc2.txt"
for dir_id,dir in enumerate(dirs):
    #inc_range=np.arange(start_inc,end_inc,step)
    handle_ranges = np.arange(start_handle_angle, end_handle_angle, step)

    if dir_id == 0:
        #continue
        original_cfg_path = original_CFG_path1
        location="0号楼"
        log_file=log_file1
    # else:
    #     break
    elif dir_id == 1:
        continue
        original_cfg_path = original_CFG_path2
        location = "1楼"
        log_file = log_file2
    else:
        continue
        original_cfg_path = original_CFG_path3
        location = "2楼平台"
        log_file = log_file3

    #TODO:  增加变量记录最优解
    for handle_range in handle_ranges:
        results = []
        res_list_2 = []
        #for inc_y in y_range:
        result = [None] * 5
        print(f"当前全站仪把手角度：x={round(handle_range,3)}")

        # signal=correct_TK(original_TK_path,total_range)
        # print(signal)
        sa.readFromCFG(original_cfg_path)
        sa.total_station_angle_cfg(handle_range)
        sa.saveFile(temp_cfg_path)
        rt = ReconstructionThread(dir, temp_cfg_path)
        #rt = ReconstructionThread(dir,dir+"//ConfigData-TkSel-new.cfg")
        rt.run()

        txt_path=os.path.join(dir,"AllGeoPoints.txt")
        temp_txt_path=txt_path.replace(".txt",f"_hands_{round(handle_range,3)}.txt")
        if os.path.isfile(txt_path):
            shutil.move(txt_path,temp_txt_path)
            clac_t=ClacTestThread(temp_txt_path,clac_txt_dirs[dir_id])#比较对应位置的误差
            a,out_strs=clac_t.run()
            print(np.abs(a).mean(), np.abs(a).max(), a.std())
            print(out_strs)
            result[0]=location
            result[1]=f"{round(handle_range,3)}"
            result[2]=np.abs(a).mean()
            result[3] = np.abs(a).max()
            result[4] =a.std()
            results.append(result)


            print(f"{results}+'\n'")
            #TODO：拿到的值怎么来获取最低值？a
            with open(log_file,"a+",encoding='utf-8') as f:
                for out_str in out_strs:
                    f.write(f"全站仪:{round(handle_range,3)}:{str(out_str)}\n")
                #f.write(f"全站仪:{round(total_range,4)}:平均误差：{np.abs(a).mean()}，最大误差：{np.abs(a).max()},标准误差：{ a.std()}\n")
'''
    for res_list in results:
        res_list_2.append(res_list[4])
    if res_list_2:
        min_value=min(res_list_2)
        min_index=res_list_2.index(min_value)
        for i, res_list in enumerate(results):
            if res_list[4] == min_value:
                print(f"最小标准误差数据：{results[i]}")

                with open(log_file2, "a+",encoding='utf-8') as f:
                    f.write(str(results[i]) + "\n")

            else:
                print("查询失败")

'''



