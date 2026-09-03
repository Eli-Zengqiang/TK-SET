# -*- coding: utf-8 -*-

from CfgClass import CfgClass
from reconstruction import ReconstructionThread
import numpy as np
import shutil
import os
from correct_tk import correct_TK
from clac_test import ClacTestThread

#0.0189
start_inc=0
end_inc=0.5
step=0.01

#inc_range=np.array(start_inc,end_inc,step)
original_TK_path1=r"E:\2.1SE-T32\2.1采集数据\CE56\2024-06-24_10-31-28-inc2\ZSHY.TK"
original_TK_path2=r"E:\2.1SE-T32\2.1采集数据\CE56\2024-06-24_10-16-35-1楼-inc2\ZSHY.TK"
original_TK_path3=r"E:\2.1SE-T32\2.1采集数据\CE56\2024-06-24_11-15-18-2楼-inc2\ZSHY.TK"


original_TK_path=r"D:\pythonProject\test\pythonProject\smart_eye2_1\out.TK"
dirs=[r"E:\2.1SE-T32\2.1采集数据\CE56\2024-06-24_10-31-28-inc2/",r"E:\2.1SE-T32\2.1采集数据\CE56\2024-06-24_10-16-35-1楼-inc2/",r"E:\2.1SE-T32\2.1采集数据\CE56\2024-06-24_11-15-18-2楼-inc2/"]
#dirs需要与clac_txt_dirs一一对应
clac_txt_dirs=[r"C:\Users\ZHXR\Desktop\2.1data\tool_or_script\标定工具v1.1_20240522\main\exe\DyCheck\0号楼",
               r"C:\Users\ZHXR\Desktop\2.1data\tool_or_script\标定工具v1.1_20240522\main\exe\DyCheck\1楼",
               r"C:\Users\ZHXR\Desktop\2.1data\tool_or_script\标定工具v1.1_20240522\main\exe\DyCheck\创新大厦2楼平台"]


log_file0=r"E:\2.1SE-T32\2.1采集数据\CE56\2024-06-24_10-16-35-1楼-inc2\inc2.txt"
log_file1=r"E:\2.1SE-T32\2.1采集数据\CE56\2024-06-24_11-15-18-2楼-inc2\inc2.txt"
log_file2=r"E:\2.1SE-T32\2.1采集数据\CE56\2024-06-24_11-15-18-2楼-inc2\inc2.txt"


for dir_id,dir in enumerate(dirs):
    inc_range=np.arange(start_inc,end_inc,step)

    if dir_id == 0:
        #continue
        original_TK_path = original_TK_path1
        location="0号楼"
        log_file = log_file0
    # else:

    elif dir_id == 1:
        break
        original_TK_path = original_TK_path2
        location = "1楼"
        log_file=log_file1
    else:
        break
        original_TK_path = original_TK_path3
        location = "2楼平台"
        log_file = log_file2

    #TODO:  增加变量记录最优解
    for inc in inc_range:
        results = []
        res_list_2 = []
        #for inc_y in y_range:
        result = [None] * 5
        print(f"当前倾角仪角度设置：x={round(inc,3)}")

        signal=correct_TK(original_TK_path,inc)
        print(signal)

        rt=ReconstructionThread(dir,dir+"//ConfigData-TkSel-new.cfg")
        rt.run()

        txt_path=os.path.join(dir,"AllGeoPoints.txt")
        temp_txt_path=txt_path.replace(".txt",f"_inc_{round(inc,3)}.txt")
        if os.path.isfile(txt_path):
            shutil.move(txt_path,temp_txt_path)
            clac_t=ClacTestThread(temp_txt_path,clac_txt_dirs[dir_id])#比较对应位置的误差
            a,out_strs=clac_t.run()
            print(np.abs(a).mean(), np.abs(a).max(), a.std())
            print(out_strs)
            result[0]=location
            result[1]=f"{round(inc,3)}"
            result[2]=np.abs(a).mean()
            result[3] = np.abs(a).max()
            result[4] =a.std()
            results.append(result)


            print(f"{results}+'\n'")
            #TODO：拿到的值怎么来获取最低值？a
            with open(log_file,"a+",encoding='utf-8') as f:
                for out_str1 in out_strs:
                    f.write(f"inc:{round(inc,3)} {str(out_str1)}"+"\n")
                # f.write(f"inc:{round(inc,3)}:平均误差：{np.abs(a).mean()}，最大误差：{np.abs(a).max()},标准误差：{ a.std()}\n")

    # for res_list in results:
    #     res_list_2.append(res_list[4])
    # if res_list_2:
    #     min_value=min(res_list_2)
    #     min_index=res_list_2.index(min_value)
    #     for i, res_list in enumerate(results):
    #         if res_list[4] == min_value:
    #             print(f"最小标准误差数据：{results[i]}")
    #
    #             with open(log_file2, "a+",encoding='utf-8') as f:
    #                 f.write(str(results[i]) + "\n")
    #
    #         else:
    #             print("查询失败")





