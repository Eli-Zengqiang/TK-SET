import os

import numpy as np

#读取全站仪打点形成2维度列表
def read_station_points(paths):
    datas1=[]
    with open (paths,'r',encoding='utf-8') as f:
        while True:
            data = f.readline().strip()
            data =data.rstrip()
            #print(data)
            if data:
                if ',' in data:
                    data=data.split(',')[0:3]  #data.split(' ')[0:3]
                else:
                    data=data.split(' ')[0:3]
                #data = data.split(',')[1:4]
                #print(data)
                datas1.append(data)
            else:
                break

    # print(datas1)
    # datas1=list(reversed(datas1))  #将文件倒序
    print(f"全站仪打点：{datas1}")
    return datas1
#计算棱镜杆左右两棱镜的距离
def cacl_twopoints_distance(datas):
    lists=[]
    num=int(len(datas) / 2)
    for i  in range(num):
        data0=np.array(datas[2*i],dtype=float)
        data1 = np.array(datas[2 * i+1],dtype=float)
        list=np.linalg.norm(data1-data0)
        lists.append(list)
        lists_arry=np.array(lists)
    print(lists)

    print(f"棱镜距离：平均数为{np.mean(lists_arry)}")

if __name__ == "__main__":
    paths = r"F:\2.1SE-T32\2.1data\20250508C75FCC55\测试数据/全站仪数据.txt" # 220241024002_1
    datas=read_station_points(paths)
    #cacl_twopoints_distance(datas)

