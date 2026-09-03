import math
import numpy as np
import matplotlib.pyplot as plt

#a=[0.5391,0.5485,0.5435,0.5523,0.5166,0.545,0.526,0.5564,0.5395]
#a=[0.5391,0.5485,0.5435,0.5523,0.545,0.526,0.5395]

#number2=list(range(1,number1+1,1))
# number2=[16.5, 19.6, 21.4, 23.5, 25.5, 27.8, 29.6, 32.4, 34.5]
a=[-0.028, 0.0, -0.028, 0.0, 0.028, -0.028, -0.028, 0.0, -0.028, -0.056, -0.045, -0.028, -0.056, -0.112, -0.084, -0.112]
number1=len(a)
#number2=list(range(1,number1+1,1))
number2=list(range(1,number1+1))
#number2=[11, 13, 15, 17, 19, 21, 23, 24, 24, 23, 21, 19, 17, 15, 14, 12, 11]
data = np.array(a)

# 计算平均值
mean_val = np.mean(data)

# 计算方差（默认是总体方差）
var_val = np.var(data)

# 如果你想要样本方差（分母是n-1），可以指定ddof=1
sample_var_val = np.var(data, ddof=1)

# 计算标准差
std_dev_val = np.std(data)

# 如果你想要样本标准差，同样可以指定ddof=1
sample_std_dev_val = np.std(data, ddof=1)

# 打印结果
print(f"平均数: {mean_val}")
print(f"总体方差: {var_val}")
#print(f"Variance (Sample): {sample_var_val}")
print(f"标准差: {std_dev_val}")
#print(f"Standard Deviation (Sample): {sample_std_dev_val}")

# 画图
# 创建一个新的图形

fig, ax = plt.subplots(1, 1,figsize=(10, 4))
ax.plot(number2[:],a[:],marker="o",color='red',label="第一次采集")
#ax.plot(number2[8:],a[8:],marker="o",color='green',label="第二次采集")
plt.rcParams['font.sans-serif'] = ['SimHei']  # 指定默认字体
plt.rcParams['axes.unicode_minus'] = False  # 解决保存图像时负号'-'显示为方块的问题
# plt.tight_layout()
plt.title('设备重装-旋转角度')
plt.xlabel('采集次数')
plt.ylabel('旋转角角度°')
ax.legend()

for i, (x, y) in enumerate(zip(number2, a)):
    ax.text(x, y, f'{round(y,5)}', ha='right', va='bottom', fontsize=9)
#
plt.show()
