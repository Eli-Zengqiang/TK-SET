
import matplotlib.pyplot as plt
import numpy as np



class DataItem:
    def __init__(self,str_line):
        items=str_line.strip().split()
        x,z=items[0].split("_")
        self.x=float(x)
        self.z=float(z)
        self.adress=items[1]
        self.adress2 = items[2]
        self.dis=float(items[3])
        self.val1=float(items[4])
        self.val2 = float(items[5])
        self.val3 = float(items[6])
        #print(items)



def read_txt(path=r"E:\2.1SE-T32\计算误差距离\0-1-2测试结果\雷达x_z数据测试.txt"):
    total_data=[]
    with open(path,"r") as f:
        lines=f.readlines()
        for i,line in enumerate(lines):
            if i==0:#跳过第一行
                continue
            c=DataItem(line)
            total_data.append(c)

    #筛选想要画图的数据
    #TODO: 修改筛选内容、
    #TODO：1.算出最低点，打印出来，且用不同颜色在3D图中标出来
    #TODO：fig同页面显示多个子图(不同距离)
    select_adress="0号楼"
    select_adress2="楼顶部.txt"
    X=[]
    Y=[]
    Z=[]
    for data in total_data:
        if data.adress==select_adress and data.adress2==select_adress2:#判断标准
            X.append(data.x)
            Y.append(data.z)
            Z.append(data.val3)


    #画图
    # 创建一个新的图形
    fig = plt.figure()
    # 添加一个 3D 子图
    ax = fig.add_subplot(111, projection='3d')
    # 绘制一个 3D 曲面
    ax.scatter(X, Y, Z, c='r', marker='o')  # c是颜色，marker是点的形状
    # 添加标题和坐标轴标签
    ax.set_title(f"{select_adress}-{select_adress2[:-4]}")
    ax.set_xlabel("X")
    ax.set_ylabel("Z")
    ax.set_zlabel("Dis")
    # 显示图形
    plt.show()

read_txt()