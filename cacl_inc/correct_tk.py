import os
import numpy as np
import  shutil
original_TK_path1=r"E:\2.1SE-T32\2.1采集数据\CE56\2024-06-24_10-31-28-inc2\ZSHY.TK"
original_TK_path2=r"E:\2.1SE-T32\2.1采集数据\20250528-CF52雷达倾角仪测试\20240528-CF52标签测试雷达倾角仪\2024-05-27_15-32-24-1楼-inc\ZSHY.TK"
original_TK_path3=r"E:\2.1SE-T32\2.1采集数据\20250528-CF52雷达倾角仪测试\20240528-CF52标签测试雷达倾角仪\2024-05-27_18-02-43-2楼平台-inc\ZSHY.TK"
# a=[]
# a1=[]
########################
def correct_TK(original_cfg_path_c,inc_c):
    temp_TK_path = r"D:\pythonProject\test\pythonProject\smart_eye2_1\out.TK"
    tk_change="false"
    a1 = []
    with open(original_cfg_path_c,'r+',encoding="utf-8") as f:
        while True:
            a=f.readline().strip().split()
            if a:
                a1.append(a)
            else:
                break
    #
    #
    # print(a1)
    # #b=float(a1[7][0])-0.01
    # start_inc=float(a1[7][0])+0.2
    # end_inc=float(a1[7][0])-0.2
    ############################

    for i in range(6,11):
        a1[i][0]=inc_c
    print(a1[6][0])


    with open(temp_TK_path,'w',encoding="utf-8") as f:
        for a1_list in a1:
            line=' '.join(map(str,a1_list))
            f.write(line+'\n')

    tk_change="true"
    #os.remove(r"E:\2.1SE-T32\2.1采集数据\20250528-CF52雷达倾角仪测试\20240528-CF52标签测试雷达倾角仪\2024-05-27_16-08-14-0楼\ZSHY.TK")
    os.remove(original_cfg_path_c)
    shutil.move(temp_TK_path,original_cfg_path_c)
    return tk_change







