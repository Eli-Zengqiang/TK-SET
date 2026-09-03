import os

import skspatial.objects as sko
import numpy as np
import open3d as o3d
import matplotlib
matplotlib.use('Qt5Agg')
import matplotlib.pyplot as plt


total_location1=np.array([-0.2633,0.3993,-0.0738])	#0号楼
total_location2=np.array([1.2358,1.1012,0.0689])  #创新大厦2楼平台
total_location3=np.array([1.2114,0.1792,0.0307])	#1楼
total_location4=np.array([-0.0175,-0.0768,-0.0043])	#眷诚斋
total_location=np.array([1,1,1])
#文件夹路径
fold1=r"C:\Users\ZHXR\Desktop\com_tool\2.1data\testbd\全站仪数据\compare\0号楼/"
fold2=r"C:\Users\ZHXR\Desktop\com_tool\2.1data\testbd\全站仪数据\compare\创新大厦2楼平台/"
fold3=r"C:\Users\ZHXR\Desktop\com_tool\2.1data\testbd\全站仪数据\compare\1楼/"
fold4=r"C:\Users\ZHXR\Desktop\com_tool\2.1data\testbd\全站仪数据\compare\眷诚斋/"

folds =[fold1,fold2,fold3,fold4]
#fold = r"C:\Users\ZHXR\Desktop\2.1data\testbd\全站仪数据\compare\0号楼/" #件夹路径
knn_n=32 #计算点个数（如coludecomare 计算时的6points
points_TS_str=0   #1是第一列为非数据 0是直接第一列为数据
TS_files=[]
#TS_files =['四周','高处','楼顶部','地面']
# TS_file1 =['四周','高处','楼顶部','地面']
# TS_file3 =['1号墙壁','2号墙壁','3号墙壁','4号墙壁','创新1号面','创新2号面','创新高程顶部']
# TS_file2 =['地面','高程顶盖','水池','右立面1','右立面2','会堂','科技大厦']
TS_file1 =['0号楼去掉设站点和地面']
TS_file2 =['创新大厦去掉设站点和地面水池']
# TS_file3 =['2025003第一次后方交会']
# TS_file3 =['1号楼去掉设站点1']
TS_file3 =['去掉遮挡点']
TS_file4=['去掉设站点和地面']

PC_file='AllGeoPoints.txt'
# cloude_path1=r"F:\2.1SE-T32\2.1采集数据\20250115精度折线\0号楼/"
# cloude_path2=r"F:\2.1SE-T32\2.1采集数据\20250115精度折线\创新大厦2楼平台/"
# cloude_path3=r"F:\2.1SE-T32\2.1采集数据\20250115精度折线\1楼/"

# cloude_path3s=[cloude_path1,cloude_path2,cloude_path3]

cleaned_lst = []  #存储平均值
cleaned_lst_mean=[] #存储标准差
lable1=[]  #存储标签 10,20,30...

# cloude_path_lists=[]
lenth=[]
for fold in folds:
	if fold == folds[0]:
		#continue
		TS_files=TS_file1
		total_location=total_location1
		# cloude_path=cloude_path1
		print("0号楼")
	elif fold == folds[1]:
		#continue
		TS_files = TS_file2
		total_location = total_location2
		# cloude_path = cloude_path2

		print("创新大厦2楼平台")
	elif fold == folds[2]:
		#continue
		TS_files = TS_file3
		total_location = total_location3
		# cloude_path = cloude_path3
		print("1楼")
	else:
		continue
		TS_files = TS_file4
		total_location = total_location4
		# cloude_path = cloude_path3
		print("眷诚斋")

	# cloude_path_lists = []
	# #获取对应文件夹下的所有点云文件
	# cloude_paths=os.listdir(cloude_path)
	# for cloude_path1 in cloude_paths:
	# 	list = os.path.join(cloude_path, cloude_path1)
	# 	cloude_path_lists.append(list)
	# print(cloude_path_lists)

	#循环计算每个点云的距离
	# label_dict = {"10": [], "20": [], "30": [], "40": [], "50": [], ">60": []}
	label_dict = {"10": [], "20": [], "30": [], "40": []}
	#label_dict = {"10": [], "20": [], "30": [], "40": [], "50": [], "60": [], ">65": []}
	# for cloude_path_list in cloude_path_lists:
	# 	print(cloude_path_list)

	points_PC = np.loadtxt(fold + PC_file)[:, 0:3]   #读取完整点云AllGeoPoints.txt,返回NumPy数组，包含了所有点的三维坐标
	# points_PC = np.loadtxt(cloude_path_list)[:, 0:3]  # 读取完整点云AllGeoPoints.txt,返回NumPy数组，包含了所有点的三维坐标
	pc_PC = o3d.geometry.PointCloud()  # type:open3d.cpu.pybind.geometry.PointCloud #创建一个空的open3d的点云对象
	pc_PC.points = o3d.utility.Vector3dVector(points_PC)  #设置点云对象的点
	pcd_tree = o3d.geometry.KDTreeFlann(pc_PC)  #为点云对象创建KD树：KD树是一种数据结构
	#用于在多维空间中组织点，以便进行有效的搜索操作，如最近邻搜索
	points_TS_all=np.empty([0,4])

	for TS_file in TS_files:   #读取截取的点云（全站仪打点）
		ten_distance10=[]   #存储10m以内的点

		if points_TS_str:
			points_TS_str = np.loadtxt(fold + TS_file+'.txt', dtype=str, delimiter=',') #全站仪打点
			ind = np.where(points_TS_str[:, 1] != '')[0] #返回是一维数组[0 1 2 3 ...99]第二列不为0的索引行号
			points_TS = np.ones([len(ind), 6])
			points_TS[:, 0:3] = points_TS_str[ind, 1:4].astype(float)  #将算中的数据块转化为浮点数
		else:
			points_TS= np.loadtxt(fold + TS_file+'.txt')[:, 0:3]
			points_TS = np.ones([len(points_TS[:,1]), 6])
			points_TS[:, 0:3] = np.loadtxt(fold + TS_file+'.txt')[:, 0:3]

		points_v_out = []
		# print(len(points_TS))
		# label_dict = {"10": [], "20": [], "30": [], "40": [],">45": []}
		for i in range(len(points_TS)):
			[_, ind, _] = pcd_tree.search_knn_vector_3d(points_TS[i,0:3], knn_n)
			neibr_points = np.asarray(pc_PC.points)[ind]

			try:
				plane = sko.Plane.best_fit(neibr_points)
				v = plane.distance_point_signed(points_TS[i, 0:3])   #计算全站仪打点，到平面拟合的距离--取绝对值
				v=abs(v)
				#print(v)
				points_TS[i, 4]=v
				scan_dist = np.linalg.norm(points_TS[i, 0:3])  #计算设站位置到墙面点的距离

				#scan_dist = np.linalg.norm(points_TS[i, 0:3]-total_location)#计算设站位置到墙面点的距离
				print(scan_dist)
				points_TS[i, 5] = scan_dist
				if scan_dist<15:
					label_dict["10"].append(v)
					ten_distance10.append(points_TS[i,0:5])   #获取15m以内的点,可以和cloudecompare	点云对比
				elif scan_dist >= 15 and scan_dist < 25:
					label_dict["20"].append(v)

				elif scan_dist >= 25 and scan_dist < 35:
					label_dict["30"].append(v)

				elif scan_dist >= 35 and scan_dist < 45:
					label_dict["40"].append(v)
				# elif scan_dist >= 45 and scan_dist < 55:
				# 	label_dict["50"].append(v)
				# elif scan_dist >= 55 and scan_dist <= 65:
				# 	label_dict["60"].append(v)
				# else:
				# 	label_dict[">65"].append(v)

				#print(points_TS[i, 5])


				#points_v_out.append(v)
			except Exception as e:
				# print(e)
				pass
			#points_v_out = np.array(points_v_out)
			# if len(points_TS)>len(points_v_out):
			# # 	print(f"输入点数为{len(points_TS)}，参与计算的点个数为{len(points_v_out)}")
	if label_dict["10"]!=[]:
		lable1.append(10)
		if len(label_dict["10"]) > 3:
			label_dict["10"].remove(max(label_dict["10"]))
			label_dict["10"].remove(min(label_dict["10"]))
		cleaned_lst.append((np.array(label_dict["10"])).std())
		cleaned_lst_mean.append((np.array(label_dict["10"])).mean())

	if label_dict["20"]!=[]:
		lable1.append(20)
		# if len(label_dict["20"]) > 3:
		# 	label_dict["20"].remove(max(label_dict["20"]))
		# 	label_dict["20"].remove(min(label_dict["20"]))
		cleaned_lst.append((np.array(label_dict["20"])).std())
		cleaned_lst_mean.append((np.array(label_dict["20"])).mean())

	if label_dict["30"]!=[]:
		lable1.append(30)
		# if len(label_dict["30"]) > 3:
		# 	label_dict["30"].remove(max(label_dict["30"]))
		# 	label_dict["30"].remove(min(label_dict["30"]))
		cleaned_lst.append((np.array(label_dict["30"])).std())
		cleaned_lst_mean.append((np.array(label_dict["30"])).mean())
	if label_dict["40"]!=[]:
		lable1.append(40)
		# if len(label_dict["40"]) > 3:
		# 	label_dict["40"].remove(max(label_dict["40"]))
		# 	label_dict["40"].remove(min(label_dict["40"]))
		cleaned_lst.append((np.array(label_dict["40"])).std())
		cleaned_lst_mean.append((np.array(label_dict["40"])).mean())
	# if label_dict["50"]!=[]:
	# 	lable1.append(50)
	# 	# if len(label_dict["50"]) > 3:
	# 	# 	label_dict["50"].remove(max(label_dict["50"]))
	# 	# 	label_dict["50"].remove(min(label_dict["50"]))
	# 	cleaned_lst.append((np.array(label_dict["50"])).std())
	# 	cleaned_lst_mean.append((np.array(label_dict["50"])).mean())
	# if label_dict["60"]!=[]:
	# 	lable1.append(60)
	# 	# if len(label_dict["60"]) > 3:
	# 	# 	label_dict["60"].remove(max(label_dict["60"]))
	# 	# 	label_dict["60"].remove(min(label_dict["60"]))
	# 	cleaned_lst.append((np.array(label_dict["60"])).std())
	# 	cleaned_lst_mean.append((np.array(label_dict["60"])).mean())
	# if label_dict[">65"]!=[]:
	# 	lable1.append(65)
	# 	# if len(label_dict[">65"]) > 3:
	# 	# 	label_dict[">65"].remove(max(label_dict[">65"]))
	# 	# 	label_dict[">65"].remove(min(label_dict[">65"]))
	# 	cleaned_lst.append((np.array(label_dict[">65"])).std())
	# 	cleaned_lst_mean.append((np.array(label_dict[">65"])).mean())

	lenth.append(len(cleaned_lst))
			# cleaned_lst.append((np.array(label_dict["10"])).std())
			# cleaned_lst.append((np.array(label_dict["20"])).std())
			# cleaned_lst.append((np.array(label_dict["30"])).std())
			# cleaned_lst.append((np.array(label_dict["40"])).std())
			# cleaned_lst.append((np.array(label_dict[">45"])).std())
	#print(label_dict["20"])

	# cleaned_lst.append((np.array(label_dict["10"])).std())
	# cleaned_lst.append((np.array(label_dict["20"])).std())
	# cleaned_lst.append((np.array(label_dict["30"])).std())
	# cleaned_lst.append((np.array(label_dict["40"])).std())
	# cleaned_lst.append((np.array(label_dict[">45"])).std())
			# label_dict["<10"]=(np.array(label_dict["<10"])).std()
			# label_dict["10-20"] = (np.array(label_dict["10-20"])).std()
			# label_dict["20-30"] = (np.array(label_dict["20-30"])).std()
			# label_dict["30-40"] = (np.array(label_dict["30-40"])).std()
			# label_dict[">40"] = (np.array(label_dict[">40"])).std()
			# values=list(label_dict.values())
			# # 将列表转换为numpy数组
			# arr = np.array(values)
			# # 使用numpy.where将NaN替换为0
			# cleaned_arr = np.where(np.isnan(arr), 0, arr)
			#
			# # 如果你需要列表而不是数组，可以将其转换回列表
			# cleaned_lst = cleaned_arr.tolist()

			#print(cleaned_lst)

			#scan_dist=np.linalg.norm(points_TS[:,0:3],axis=1).mean()
			#points_TS_all=np.append(points_TS_all,points_TS)
		# 	print(TS_file+'('+str(round(scan_dist,1))+')最大绝对距离：'+str(np.abs(points_TS[:, 4]).max())+';平均距离：'+str(points_TS[:, 4].mean())+';标准差：'+str(points_TS[:, 4].std()))#points_TS[:,3]
		# np.savetxt(fold+'TStoPCdist.txt',points_TS_all,'%.04f')
	# for i in range(int(len(cleaned_lst)/5)):
	#
	# 	label1 = ["<10m", "10-20m", "20-30m", "30-40m", ">40m"]
	# 	fig = plt.figure(figsize=(10, 8))
	# 	plt.plot(label1,cleaned_lst[5*i:5*(i+1)])
	cleaned_lst1=np.array(cleaned_lst)
	cleaned_lst1 = np.round(cleaned_lst1, decimals=6)
	cleaned_lst=cleaned_lst1.tolist()

	cleaned_lst_mean1 = np.array(cleaned_lst_mean)
	cleaned_lst_mean1 = np.round(cleaned_lst_mean1, decimals=6)
	cleaned_lst_mean= cleaned_lst_mean1.tolist()


'''

# label1 = ["10m", "20m", "30m", "40m", ">45m"]
fig = plt.figure(figsize=(10, 8))
plt.tight_layout()
plt.rcParams['font.sans-serif'] = ['SimHei']  # 指定默认字体
plt.rcParams['axes.unicode_minus'] = False
plt.plot(lable1[0:lenth[0]],cleaned_lst_mean[0:lenth[0]],label='0号楼',color='blue')
plt.errorbar(lable1[0:lenth[0]],cleaned_lst_mean[0:lenth[0]],cleaned_lst[0:lenth[0]], fmt='o', ecolor='blue', elinewidth=2, capsize=5)

plt.plot(lable1[lenth[0]:lenth[1]],cleaned_lst_mean[lenth[0]:lenth[1]],label='创新大厦',color='red')
plt.errorbar(lable1[lenth[0]:lenth[1]],cleaned_lst_mean[lenth[0]:lenth[1]],cleaned_lst[lenth[0]:lenth[1]], fmt='o', ecolor='red', elinewidth=2, capsize=5)

plt.plot(lable1[lenth[1]:lenth[2]],cleaned_lst_mean[lenth[1]:lenth[2]],label='1号楼',color='green')
plt.errorbar(lable1[lenth[1]:lenth[2]],cleaned_lst_mean[lenth[1]:lenth[2]],cleaned_lst[lenth[1]:lenth[2]], fmt='o', ecolor='green', elinewidth=2, capsize=5)
plt.title("测试误差m")
plt.xlabel("测试距离m")
plt.ylabel("测试误差m")
plt.legend()

# for i in range(len(lable1)):  # 使用 range(len(x)) 确保不会超出索引范围
# 	plt.text(lable1[i], cleaned_lst_mean[i], str(cleaned_lst_mean[i]), ha='right', va='bottom')

for i in range(len(lable1)):  #range(len(lable1)) 使用 range(len(x)) 确保不会超出索引范围
	plt.text(lable1[i], cleaned_lst_mean[i],f'{cleaned_lst_mean[i]:.3f} ± {cleaned_lst[i]:.3f}', ha='right', va='bottom')
	# print(f'{cleaned_lst[i]:.6f} ± {cleaned_lst_mean[i]:.6f}')
# 显示图表
plt.show()
# print(f'{len(label_dict["40"])}')



#print(cleaned_lst)
'''
print(len(lable1))
print(len(cleaned_lst_mean))

fig, axs = plt.subplots(4, 1, figsize=(10, 5))
plt.tight_layout()
plt.rcParams['font.sans-serif'] = ['SimHei']  # 指定默认字体
plt.rcParams['axes.unicode_minus'] = False
axs[0].plot(lable1[0:lenth[0]], cleaned_lst_mean[0:lenth[0]], label='0号楼', color='blue')
axs[0].errorbar(lable1[0:lenth[0]], cleaned_lst_mean[0:lenth[0]], cleaned_lst[0:lenth[0]], fmt='o',
						ecolor='blue', elinewidth=2, capsize=5)
axs[1].plot(lable1[lenth[0]:lenth[1]], cleaned_lst_mean[lenth[0]:lenth[1]], label='创新大厦', color='red')
axs[1].errorbar(lable1[lenth[0]:lenth[1]], cleaned_lst_mean[lenth[0]:lenth[1]], cleaned_lst[lenth[0]:lenth[1]],
						fmt='o', ecolor='red', elinewidth=2, capsize=5)

axs[2].plot(lable1[lenth[1]:lenth[2]],cleaned_lst_mean[lenth[1]:lenth[2]],label='1号楼',color='green')
axs[2].errorbar(lable1[lenth[1]:lenth[2]],cleaned_lst_mean[lenth[1]:lenth[2]],cleaned_lst[lenth[1]:lenth[2]], fmt='o', ecolor='green', elinewidth=2, capsize=5)

# axs[3].plot(lable1[lenth[2]:lenth[3]],cleaned_lst_mean[lenth[2]:lenth[3]],label='眷诚斋',color='black')
# axs[3].errorbar(lable1[lenth[2]:lenth[3]],cleaned_lst_mean[lenth[2]:lenth[3]],cleaned_lst[lenth[2]:lenth[3]], fmt='o', ecolor='black', elinewidth=2, capsize=5)

print(lenth)
print(lable1)
for i in range(len(lable1)):  #range(len(lable1)) 使用 range(len(x)) 确保不会超出索引范围
	if i <lenth[0]:
		axs[0].text(lable1[i]+1, cleaned_lst_mean[i],f'{cleaned_lst_mean[i]:.5f} ± {cleaned_lst[i]:.5f}', ha='right', va='bottom')
	if lenth[0]<= i <lenth[1]:

		axs[1].text(lable1[i]+1, cleaned_lst_mean[i], f'{cleaned_lst_mean[i]:.5f} ± {cleaned_lst[i]:.5f}', ha='right',va='bottom')
	if lenth[1] <= i <lenth[2]:

		axs[2].text(lable1[i]+1, cleaned_lst_mean[i], f'{cleaned_lst_mean[i]:.5f} ± {cleaned_lst[i]:.5f}', ha='right',va='bottom')

	# if lenth[2] <= i <lenth[3]:
	#
	# 	axs[3].text(lable1[i]+1, cleaned_lst_mean[i], f'{cleaned_lst_mean[i]:.5f} ± {cleaned_lst[i]:.5f}', ha='right',va='bottom')
	#

# print(f'{cleaned_lst[i]:.6f} ± {cleaned_lst_mean[i]:.6f}')
# 显示图表
axs[0].set_title("测试误差m")
axs[0].set_xlabel("测试距离m")
axs[0].set_ylabel("测试误差m")
axs[0].set_ylim(-0.12, 0.12)
axs[0].set_xlim(0,50)

axs[0].legend()
# axs[1].set_title("测试误差m")
axs[1].set_xlabel("测试距离m")
axs[1].set_ylabel("测试误差m")
axs[1].set_ylim(-0.12, 0.12)
axs[1].set_xlim(0,50)
axs[1].legend()
# axs[2].set_title("测试误差m")
axs[2].set_xlabel("测试距离m")
axs[2].set_ylabel("测试误差m")
axs[2].set_ylim(-0.12, 0.12)
axs[2].set_xlim(0,50)
axs[2].legend()

axs[3].set_xlabel("测试距离m")
axs[3].set_ylabel("测试误差m")
axs[3].set_ylim(-0.12, 0.12)
axs[3].set_xlim(0,50)
axs[3].legend()

plt.show()

