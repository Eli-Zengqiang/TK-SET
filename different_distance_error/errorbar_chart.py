import matplotlib.pyplot as plt
import numpy as np

# 示例数据
x = ['创新2号面','2号墙壁','3号墙壁','创新1号面','创新高程顶部','4号墙壁','1号墙壁']# X轴数据，例如5个时间点
y1 = [-0.0042,0.00028,-0.0007,-0.0012,-0.059,-0.0014,-0.0024]
yerr1 =[0.01,0.009,0.007,0.017,0.0117,0.0070,0.040]
y2=[0.0072,0.0027,-0.0018,-0.0006,-0.004,-0.0029,-0.0011]# Y轴数据，例如在这些时间点的测量值
yerr2 = [0.004,0.0085,0.0037,0.0236,0.0023,0.0077,0.01]
# Y轴数据的误差范围
plt.figure(figsize=(8, 3))
# 绘制误差棒图
plt.errorbar(x, y1, yerr=yerr1, fmt='o', ecolor='yellow', elinewidth=2, capsize=5, label='更换雷达前-平均误差±标准差')
plt.plot(x,y1,color='yellow')

plt.errorbar(x, y2, yerr=yerr2, fmt='o', ecolor='red', elinewidth=2, capsize=5, label='更换雷达后-平均误差±标准差')
plt.plot(x,y2,color='red')
for i in range(len(x)):  # 使用 range(len(x)) 确保不会超出索引范围
	plt.text(x[i], y1[i],f'{y1[i]:.3f} ± {yerr1[i]:.3f}', ha='right', va='bottom')
	plt.text(x[i], y2[i], f'{y2[i]:.3f} ± {yerr2[i]:.3f}', ha='right', va='bottom')
	# print(f'{cleaned_lst[i]:.6f} ± {cleaned_lst_mean[i]:.6f}')

# 添加标题和标签
plt.tight_layout()
plt.rcParams['font.sans-serif'] = ['SimHei']  # 指定默认字体
plt.rcParams['axes.unicode_minus'] = False
plt.title('距离-精度误差棒')
plt.xlabel('采集位置')
plt.ylabel('采集误差m')

# 显示图例
plt.legend()

# 显示网格
plt.grid(True)

# 显示图表
plt.show()