import numpy as np
import os
import math
import matplotlib.pyplot as plt
##################左右棱镜球的质心到周边点的距离###################################

a=1 #徕卡TS16,a=2,是左侧棱镜（高的那个），1是右侧棱镜
#data_path=input("输入路径\n")
#data_path=r"E:\2.1SE-T32\2.1采集数据\20241022会堂棱镜常数\徕卡圆棱镜\徕卡圆棱镜.txt"
data_path=r"E:\2.1SE-T32\2.1采集数据\20241030詹天佑重装\全站仪打点\20241030001.txt"
#"E:\2.1SE-T32\2.1采集数据\20241022会堂棱镜常数\徕卡圆棱镜\徕卡圆棱镜.txt"
#"E:\2.1SE-T32\2.1采集数据\20241022会堂棱镜常数\360度棱镜\360棱镜.txt"
# "E:\2.1SE-T32\2.1采集数据\20241018棱镜球\29.txt"
# "E:\2.1SE-T32\2.1采集数据\20241018棱镜球\30.txt"
total_station_datas=np.loadtxt(data_path,delimiter=',')[:,1:4]
total_station_datas=np.round(total_station_datas,decimals=4)

print(total_station_datas)
# 获取数组的行数和列数
num_rows, num_cols = total_station_datas.shape
numbers=int(num_rows/2)
#numbers=int(num_rows)

print(num_rows)
left_datas = np.empty((numbers, num_cols))
# left_datas = np.empty((int((num_rows)/2), num_cols))
right_datas= np.empty((numbers, num_cols))
for i in range(numbers):
    left_datas[i]=total_station_datas[2*i,:]
    right_datas[i]=total_station_datas[2*i+1,:]

angle=list(range(8,(numbers+1)*2+6,2))
print(angle)
#徕卡TS16,a=2,是左侧棱镜，1是右侧棱镜

if a==1:
    left_datas=left_datas[:,:]
    print("右边棱镜")
    #left_datas = total_station_datas[:, :]

else:
    left_datas = right_datas[:, :]
    print("左边棱镜")

# angle=['上30','上60','上90','上120','上135','外30','外60','外90','外120']
#angle=['上30','上60','上90','上120','上135','外30','外60','外90','外120','外135']
#angle=['0-0','0','45','135','180','225','315']
#angle=['0','45','135','180','225','315']
# 创建一个包含3个子画布的图形
fig, axs = plt.subplots(3, 1, figsize=(10, 15))  # 3行1列，调整figsize以适应布局
left_data_list=[]
title=['x坐标','y坐标','z坐标']
# 遍历数组的每一列，并在每个子画布上绘制折线图(将一列数据分为6组)
# for i, col in enumerate(array.T ):  # array.T 是数组的转置，这样我们可以按列迭代
#     axs[i].plot(angle,left_datas[:,i], marker='o')  # 使用'o'标记数据点
# colors=['red','orange', 'yellow', 'green', 'cyan', 'blue', 'purple']
# labels=['27mm','28mm','29mm','30mm','31mm','32mm']
# for j in range(6):
#     for i in range(3):  # array.T 是数组的转置，这样我们可以按列迭代
#         left_data_list = left_datas[:, i].tolist()
#         axs[i].plot(angle,left_data_list[6*j:6*(j+1)], marker='o',color=colors[j],label=labels[j])  # 使用'o'标记数据点
#         # 'orange', 'yellow', 'green', 'cyan', 'blue', 'purple', 'black', 'violet', 'brown'
#         # axs[i].plot(angle, left_data_list[6:12], marker='o', color='orange',label='28mm')
#         # axs[i].plot(angle, left_data_list[12:18], marker='o', color='yellow',label='29mm')
#         # axs[i].plot(angle, left_data_list[18:24], marker='o', color='cyan',label='30mm')
#         # axs[i].plot(angle, left_data_list[24:30], marker='o', color='blue',label='31mm')
#         # axs[i].plot(angle, left_data_list[30:36], marker='o', color='purple',label='32mm')
#         axs[i].set_title(f'{title[i]}')  # 设置子画布的标题
#         axs[i].grid(True)  # 显示网格
#         axs[i].set_xlabel('角度(°)')  # 设置x轴标签（行索引）
#         axs[i].set_ylabel('距离(m)')  # 设置y轴标签（值）
#         axs[i].legend() #生成图例
#         for z, (x, y) in enumerate(zip(angle, left_data_list[6*j:6*(j+1)])):
#             axs[i].text(x, y, f'{round(y, 5)}', ha='right', va='bottom', fontsize=9)



for i in range(3):  # array.T 是数组的转置，这样我们可以按列迭代
    left_data_list = left_datas[:, i].tolist()
    axs[i].plot(angle,left_data_list, marker='o',color='green')  # 使用'o'标记数据点
    # 'orange', 'yellow', 'green', 'cyan', 'blue', 'purple', 'black', 'violet', 'brown'
    # axs[i].plot(angle, left_data_list[6:12], marker='o', color='orange',label='28mm')
    # axs[i].plot(angle, left_data_list[12:18], marke
    # r='o', color='yellow',label='29mm')
    # axs[i].plot(angle, left_data_list[18:24], marker='o', color='cyan',label='30mm')
    # axs[i].plot(angle, left_data_list[24:30], marker='o', color='blue',label='31mm')
    # axs[i].plot(angle, left_data_list[30:36], marker='o', color='purple',label='32mm')
    axs[i].set_title(f'{title[i]}')  # 设置子画布的标题
    axs[i].grid(True)  # 显示网格
    axs[i].set_xlabel('全站仪到棱镜距离(m)')  # 设置x轴标签（行索引）
    axs[i].set_ylabel('打点坐标(m)')  # 设置y轴标签（值）
    #axs[i].legend() #生成图例
    for z, (x, y) in enumerate(zip(angle, left_data_list)):
        axs[i].text(x, y, f'{round(y, 5)}', ha='right', va='bottom', fontsize=9)


    # 调整子画布之间的间距
plt.rcParams['font.sans-serif'] = ['SimHei']  # 指定默认字体
plt.rcParams['axes.unicode_minus'] = False  # 解决保存图像时负号'-'显示为方块的问题
plt.tight_layout()

# 显示图形

plt.savefig('angle_distance.png')
plt.show()



fig, ax = plt.subplots(1, 1)
#绘制质心到周边点的距离（将一列数据分为6组）
# for j in range(6):
#
#     left_center = []
#     for i in range(3):
#         left_data=left_datas[:,i]
#         mean=np.mean(left_data)
#         left_center.append(mean)
#         var=np.var(left_data)
#         std=np.std(left_data)
#         print(f"棱镜： 平均数为：{mean}  方差为：{var}  标准差为：{std}")
#     #print("\n")
#     # right_center=[]
#     # for i in range(0, 3):
#     #     right_data = right_datas[:, i]
#     #
#     #     mean1 = np.mean( right_data)
#     #     right_center.append(mean1)
#     #     var1 = np.var( right_data)
#     #     std1 = np.std( right_data)
#     #     print(f"右边棱镜： 平均数为：{mean1}  方差为：{var1}  标准差为：{std1}")
#         #print(left_data)
#     a=np.array(left_center)
#     distances=[]
#     #for i in range(int((num_rows)/2)):
#     for i in range(6*j,6*(j+1)):
#         distance=np.linalg.norm(left_datas[i] - a)
#         distances.append(distance)
#
#     distances1=np.array(distances)
#     print(distances)
#     print(f"质心到周边的平均距离:{round(distances1.mean(),5)},方差:{distances1.var()},标准差:{round(distances1.std(),5)}")
#     print('\n')
#     #angle=['上30','上60','上90','上120','上135','外30','外60','外90','外120','外135']
#     #angle=['0-0','0','45','135','180','225','315']
#     #angle=['0','45','135','180','225','315']
#     # plt.figure()
#     # plt.rcParams['font.sans-serif'] = ['SimHei']  # 指定默认字体
#     # plt.rcParams['axes.unicode_minus'] = False  # 解决保存图像时负号'-'显示为方块的问题
#     ax.plot(angle,distances,marker="o",color=colors[j],label=labels[j])
#     plt.title('3维点到质心距离')
#     plt.xlabel('角度(°)')
#     plt.ylabel('距离(m)')
#     ax.legend()   #生成图例
#     for i, (x, y) in enumerate(zip(angle, distances)):
#         ax.text(x, y, f'{round(y,5)}', ha='right', va='bottom', fontsize=9)




left_center = []
for i in range(3):
    left_data=left_datas[:,i]
    mean=np.mean(left_data)
    left_center.append(mean)
    var=np.var(left_data)
    std=np.std(left_data)
    print(f"棱镜： 平均数为：{mean}  方差为：{var}  标准差为：{std}")

a=np.array(left_center)
distances=[]
#for i in range(int((num_rows)/2)):
for i in range(numbers):
    distance=np.linalg.norm(left_datas[i] - a)
    distances.append(distance)
distances.remove(max(distances))

distances1=np.array(distances)
print(distances)
print(f"质心到周边的平均距离:{round(distances1.mean(),5)},方差:{distances1.var()},标准差:{round(distances1.std(),5)}")
print('\n')
#angle=['上30','上60','上90','上120','上135','外30','外60','外90','外120','外135']
#angle=['0-0','0','45','135','180','225','315']
#angle=['0','45','135','180','225','315']
# plt.figure()
# plt.rcParams['font.sans-serif'] = ['SimHei']  # 指定默认字体
# plt.rcParams['axes.unicode_minus'] = False  # 解决保存图像时负号'-'显示为方块的问题
ax.plot(angle,distances,marker="o",color='red')
plt.title('3维点到质心距离')
plt.xlabel('全站仪到棱镜距离(m)')
plt.ylabel('3维点到质心距离(m)')
#ax.legend()   #生成图例
for i, (x, y) in enumerate(zip(angle, distances)):
    ax.text(x, y, f'{round(y,5)}', ha='right', va='bottom', fontsize=9)
# 显示图形

plt.savefig(r'D:\pythonProject\test\pythonProject\smart_eye2_1\test\distance.jpg')
plt.show()