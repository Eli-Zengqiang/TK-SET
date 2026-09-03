import os
import re
import matplotlib.pyplot as plt

txt_path1= "D:\Eli\smarteye2.1\充电测试.txt"
txt_path2 = "D:\Eli\smarteye2.1\放电测试.txt"


#读取数据成列表
def read_datas(path):
    datas=[]
    with open(path,'r',encoding='utf-8') as f:
        while True:
            data = f.readline().rstrip()
            if data:
                data1 = re.sub(r'[, ]',',',data).split(",")
                datas.append(data1)
            else:
                break

    #print(datas)
    return datas


#读取数据后，计算输入功率
def cal_input_power(datas):
    power_sums=0
    for i in range(2,len(datas)-1):
        power_sum=0
        power_sum=((float(datas[i][3])/1000)*(abs(float(datas[i][4]))/1000)+(float(datas[i+1][3])/1000)*(abs(float(datas[i+1][4]))/1000))*250/1000/3600/2 #5(1/3600)秒化时
        #power_sum=((float(datas[i][3])/1000)*(abs(float(datas[i][4]))/1000)+(float(datas[i+1][3])/1000)*(abs(float(datas[i+1][4]))/1000))*5000/1000/3600/2
        power_sums=power_sums+power_sum
    print(f"输入功率：{power_sums}")

#读取数据后，计算输入功率
def cal_output_power(datas):
    power_sums=0
    for i in range(2,len(datas)-1):
        power_sum=0
        #power_sum=((float(datas[i][3])/1000)*(abs(float(datas[i][4]))/1000)+(float(datas[i+1][3])/1000)*(abs(float(datas[i+1][4]))/1000))*250/1000/3600/2 #5(1/3600)秒化时
        power_sum=((float(datas[i][3])/1000)*(abs(float(datas[i][4]))/1000)+(float(datas[i+1][3])/1000)*(abs(float(datas[i+1][4]))/1000))*5000/1000/3600/2
        power_sums=power_sums+power_sum
    print(f"输出功率：{power_sums}")


#将数据时间截取，获得时间，电量列表
def change_data(a):
    c=[]
    for i in range(2, len(a)):
        b= a[i][1].split(':')
        b=b[0:2]
        b.append(int(a[i][2]))
        for j in range(0, len(b)):
            b[j] = int(b[j])
        c.append(b)
    print(c)
    print()

    e = []
    n = 1
    for i in range(0, len(c)):
        if i < n:
            if i == 0:
                e.append(c[i])
                print(e)
            continue
        else:
            for j in range(i, len(c)):
                    d0 = c[i][0]
                    d1 = c[i][1] + 20      #每隔20min提取一个值
                    if d1 >= 60:
                        d1 = d1 - 60
                        d0 = c[i][0] + 1
                    if j==i:
                        continue
                    else:
                        if c[j][0] == d0 and c[j][1] == d1:
                            n = j
                            e.append(c[j])
                            break
    #print(e)
    time_voltages=[]

    for i in e:
        time_voltage = []
        time=f"{i[0]}:{i[1]}"
        '''

        if len(time) <5:
            time = time[0:3]+'0'+time[3]
        '''

        time_voltage.append(time)
        time_voltage.append(i[2])
        time_voltages.append(time_voltage)

    print(time_voltages)
    return time_voltages



def make_plot(datas):
    V = []
    H = []
    dem_data=[]
    for i in range(0, len(datas)):
            H.append(datas[i][0])
            V.append(datas[i][1])
    #设置画布
    plt.figure(figsize=(18, 10))

    plt.plot(H,V,c='r')
    # 设置全局字体，注意楷体'KaiTi'
    plt.rcParams['font.sans-serif'] = ['KaiTi']
    # 设置符号修正
    plt.rcParams['axes.unicode_minus'] = False

    # 显示坐标
    for i in range(len(V)):
        plt.text(H[i], V[i], str(V[i]))

    #旋转x轴坐标
    plt.xticks(rotation= 270)
    # 添加标题和坐标轴标签
    # 添加标题和坐标轴标签
    plt.title("电量测试")
    plt.xlabel("放电时间")
    plt.ylabel("电量百分比")

    plt.savefig('放电测试.png')
    # 显示图形
    plt.show()


def main():
    a=read_datas(txt_path1)
    cal_input_power(a)
    #make_plot(b)

main()
