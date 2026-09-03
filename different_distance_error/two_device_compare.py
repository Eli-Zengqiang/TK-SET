import os

import numpy
import skspatial.objects as sko
import numpy as np
import open3d as o3d
import matplotlib.pyplot as plt
import matplotlib.transforms as transforms

def two_devie(display1,display2,display3,display4,data_fold = r"G:\TK-set\2.1data\20251105两台设备验证360\CF23\180-360\180-360回归眷诚斋"):
	total_location0=np.array([-0.7504,0.6302,-0.0813])	#0号楼
	total_location2=np.array([1.6351,1.0425,0.0923])  #创新大厦2楼平台
	total_location1=np.array([2.7550,4.5043,0.0877])	#1楼
	total_location4=np.array([-0.0001,0.0001,-0.0001])
	total_location=np.array([1,1,1])
	#文件夹路径
	fold0=r"C:\Users\ZHXR\Desktop\com_tool\2.1data\testbd\全站仪数据\compare\0号楼/"
	fold2=r"C:\Users\ZHXR\Desktop\com_tool\2.1data\testbd\全站仪数据\compare\创新大厦2楼平台/"
	fold1=r"C:\Users\ZHXR\Desktop\com_tool\2.1data\testbd\全站仪数据\compare\1楼/"
	fold3=r"C:\Users\ZHXR\Desktop\com_tool\2.1data\testbd\全站仪数据\compare\眷诚斋/"
	folds =[fold0,fold1,fold2,fold3]
	datas_paths=[]
	#data_fold = r"G:\TK-set\2.1data\20251105两台设备验证360\CF23\180-360\180-360回归眷诚斋"
	data_fold=data_fold
	data_fold1=os.listdir(data_fold)

	for data in data_fold1:
		data_folds=os.path.join(data_fold,data)
		datas_paths.append(data_folds)
	datas_paths=sorted(datas_paths)
	print(datas_paths)
	knn_n = 32  # 计算点个数（如coludecomare 计算时的6points
	points_TS_str = 0  # 1是第一列为非数据 0是直接第一列为数据

	TS_file0 = '0号楼去掉设站点.txt'
	TS_file1 = '去掉遮挡点.txt'
	TS_file2 = '创新大厦去掉设站点.txt'
	TS_file3 = '去掉设站点.txt'
	two_cleaned_lst = []  # 存储平均值
	two_cleaned_lst_mean = []  # 存储标准差
	lable1 = []  # 存储标签 10,20,30...
	for id,data_folder in enumerate (datas_paths):
		cleaned_lst = []  # 存储平均值
		cleaned_lst_mean = []  # 存储标准差
		lenth = []
		for i in range(0,4):
			PC_file=os.path.join(data_folder,f'AllGeoPoints{i}.txt')
			print(PC_file)

			if i == 0 :
				TS_file=fold0+TS_file0
				print("0号楼")
			elif i == 1 :
				TS_file=fold1+TS_file1
				print("1号楼")
			elif i == 2:
				TS_file=fold2+TS_file2
				print("创新大厦2楼平台")
			else:
				TS_file=fold3+TS_file3
				print("眷诚斋")


			label_dict = {"10": [], "20": [], "30": [], "40": []}
			# label_dict = {"10": [], "20": [], "30": [], "40": [], "50": [], "60": [], ">65": []}
			# for cloude_path_list in cloude_path_lists:
			# 	print(cloude_path_list)

			points_PC = np.loadtxt(PC_file)[:, 0:3]   #读取完整点云AllGeoPoints.txt,返回NumPy数组，包含了所有点的三维坐标
			# points_PC = np.loadtxt(cloude_path_list)[:, 0:3]  # 读取完整点云AllGeoPoints.txt,返回NumPy数组，包含了所有点的三维坐标
			pc_PC = o3d.geometry.PointCloud()  # type:open3d.cpu.pybind.geometry.PointCloud #创建一个空的open3d的点云对象
			pc_PC.points = o3d.utility.Vector3dVector(points_PC)  #设置点云对象的点
			pcd_tree = o3d.geometry.KDTreeFlann(pc_PC)  #为点云对象创建KD树：KD树是一种数据结构
			#用于在多维空间中组织点，以便进行有效的搜索操作，如最近邻搜索
			points_TS_all=np.empty([0,4])
		#####原本的for循环，更换全站仪文件夹

			ten_distance10=[]   #存储10m以内的点

			if points_TS_str:
				points_TS_str = np.loadtxt(TS_file, dtype=str, delimiter=',') #全站仪打点
				ind = np.where(points_TS_str[:, 1] != '')[0] #返回是一维数组[0 1 2 3 ...99]第二列不为0的索引行号
				points_TS = np.ones([len(ind), 6])
				points_TS[:, 0:3] = points_TS_str[ind, 1:4].astype(float)  #将算中的数据块转化为浮点数
			else:
				points_TS= np.loadtxt(TS_file)[:, 0:3]
				points_TS = np.ones([len(points_TS[:,1]), 6])
				points_TS[:, 0:3] = np.loadtxt(TS_file)[:, 0:3]

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

					#scan_dist = np.linalg.norm(points_TS[i, 0:3]-total_location)
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
		two_cleaned_lst.append(cleaned_lst)  # 存储标准差
		two_cleaned_lst_mean.append(cleaned_lst_mean) # 存储平均值
	# two_cleaned_lst_mean[1]=np.array(two_cleaned_lst_mean[1])+0.05
	# two_cleaned_lst_mean[1]=two_cleaned_lst_mean[1].tolist()



	print(lenth)
	# print(len(lable1))
	print(len(cleaned_lst_mean))
	print(f"lable1:{lable1}")
	print(f"two_cleaned_lst标准差:{two_cleaned_lst}")
	print(f"two_cleaned_lst_mean平均值:{two_cleaned_lst_mean}")

	fig, axs = plt.subplots(2, 2, figsize=(10, 5))
	plt.tight_layout()
	plt.rcParams['font.sans-serif'] = ['SimHei']  # 指定默认字体
	plt.rcParams['axes.unicode_minus'] = False

	#设备1：two_cleaned_lst_mean[0]，0号楼：0:lenth[0]
	axs[0,0].plot(lable1[0:lenth[0]], two_cleaned_lst_mean[0][0:lenth[0]], label=display1, color='blue')
	axs[0,0].errorbar(lable1[0:lenth[0]], two_cleaned_lst_mean[0][0:lenth[0]], two_cleaned_lst[0][0:lenth[0]], fmt='o',
							ecolor='blue', elinewidth=2, capsize=5)
	#设备2：
	axs[0,0].plot(lable1[0:lenth[0]], two_cleaned_lst_mean[1][0:lenth[0]], label=display2, color='red')
	axs[0,0].errorbar(lable1[0:lenth[0]],two_cleaned_lst_mean[1][0:lenth[0]], two_cleaned_lst[1][0:lenth[0]], fmt='o',
							ecolor='red', elinewidth=2, capsize=5)
	if len(data_fold1) > 2:
	#设备3
		axs[0,0].plot(lable1[0:lenth[0]], two_cleaned_lst_mean[2][0:lenth[0]], label=display3, color='green')
		axs[0,0].errorbar(lable1[0:lenth[0]],two_cleaned_lst_mean[2][0:lenth[0]], two_cleaned_lst[2][0:lenth[0]], fmt='o',
								ecolor='green', elinewidth=2, capsize=5)
		#设备4
		axs[0,0].plot(lable1[0:lenth[0]], two_cleaned_lst_mean[3][0:lenth[0]], label=display4, color='black')
		axs[0,0].errorbar(lable1[0:lenth[0]],two_cleaned_lst_mean[3][0:lenth[0]], two_cleaned_lst[3][0:lenth[0]], fmt='o',
								ecolor='black', elinewidth=2, capsize=5)

	# 设备1，1楼：lenth[0]:lenth[1]
	axs[0,1].plot(lable1[lenth[0]:lenth[1]],two_cleaned_lst_mean[0][lenth[0]:lenth[1]],label=display1, color='blue')
	axs[0,1].errorbar(lable1[lenth[0]:lenth[1]],two_cleaned_lst_mean[0][lenth[0]:lenth[1]],two_cleaned_lst[0][lenth[0]:lenth[1]],
					fmt='o', ecolor='blue', elinewidth=2, capsize=5)#capsize=5,transform=trans

	# fig = axs[0,1].figure
	# dpi = fig.dpi
	# offset = transforms.ScaledTranslation(0, 1 / 2.54, fig.dpi_scale_trans)  # 1cm = 1/2.54英寸
	# trans = axs[0,1].transData + offset
	# 设备2
	axs[0,1].plot(lable1[lenth[0]:lenth[1]],two_cleaned_lst_mean[1][lenth[0]:lenth[1]],label=display2, color='red')
	axs[0,1].errorbar(lable1[lenth[0]:lenth[1]],two_cleaned_lst_mean[1][lenth[0]:lenth[1]],two_cleaned_lst[1][lenth[0]:lenth[1]],
					fmt='o', ecolor='red', elinewidth=2, capsize=5)
	if len(data_fold1) > 2:
	# 设备3
		axs[0,1].plot(lable1[lenth[0]:lenth[1]],two_cleaned_lst_mean[2][lenth[0]:lenth[1]],label=display3, color='green')
		axs[0,1].errorbar(lable1[lenth[0]:lenth[1]],two_cleaned_lst_mean[2][lenth[0]:lenth[1]],two_cleaned_lst[2][lenth[0]:lenth[1]],
						fmt='o', ecolor='green', elinewidth=2, capsize=5)

		# 设备4
		axs[0,1].plot(lable1[lenth[0]:lenth[1]],two_cleaned_lst_mean[3][lenth[0]:lenth[1]],label=display4, color='black')
		axs[0,1].errorbar(lable1[lenth[0]:lenth[1]],two_cleaned_lst_mean[3][lenth[0]:lenth[1]],two_cleaned_lst[3][lenth[0]:lenth[1]],
						fmt='o', ecolor='black', elinewidth=2, capsize=5)

	# 设备1,2楼
	axs[1,0].plot(lable1[lenth[1]:lenth[2]], two_cleaned_lst_mean[0][lenth[1]:lenth[2]], label=display1, color='blue')
	axs[1,0].errorbar(lable1[lenth[1]:lenth[2]],two_cleaned_lst_mean[0][lenth[1]:lenth[2]], two_cleaned_lst[0][lenth[1]:lenth[2]],
							fmt='o', ecolor='blue', elinewidth=2, capsize=5)


	axs[1,0].plot(lable1[lenth[1]:lenth[2]], two_cleaned_lst_mean[1][lenth[1]:lenth[2]], label=display2, color='red')
	axs[1,0].errorbar(lable1[lenth[1]:lenth[2]], two_cleaned_lst_mean[1][lenth[1]:lenth[2]], two_cleaned_lst[1][lenth[1]:lenth[2]],
							fmt='o', ecolor='red', elinewidth=2, capsize=5)
	if len(data_fold1) > 2:

		axs[1,0].plot(lable1[lenth[1]:lenth[2]], two_cleaned_lst_mean[2][lenth[1]:lenth[2]], label=display3, color='green')
		axs[1,0].errorbar(lable1[lenth[1]:lenth[2]], two_cleaned_lst_mean[2][lenth[1]:lenth[2]], two_cleaned_lst[2][lenth[1]:lenth[2]],
								fmt='o', ecolor='green', elinewidth=2, capsize=5)

		axs[1,0].plot(lable1[lenth[1]:lenth[2]], two_cleaned_lst_mean[3][lenth[1]:lenth[2]], label=display4, color='black')
		axs[1,0].errorbar(lable1[lenth[1]:lenth[2]], two_cleaned_lst_mean[3][lenth[1]:lenth[2]], two_cleaned_lst[3][lenth[1]:lenth[2]],
								fmt='o', ecolor='black', elinewidth=2, capsize=5)

	axs[1,1].plot(lable1[lenth[2]:lenth[3]], two_cleaned_lst_mean[0][lenth[2]:lenth[3]], label=display1, color='blue')
	axs[1,1].errorbar(lable1[lenth[2]:lenth[3]],two_cleaned_lst_mean[0][lenth[2]:lenth[3]], two_cleaned_lst[0][lenth[2]:lenth[3]],
							fmt='o', ecolor='blue', elinewidth=2, capsize=5)

	# fig = axs[1,1].figure
	# dpi = fig.dpi
	# offset = transforms.ScaledTranslation(0, 1 / 2.54, fig.dpi_scale_trans)  # 1cm = 1/2.54英寸
	# trans = axs[1,1].transData + offset
	axs[1,1].plot(lable1[lenth[2]:lenth[3]], two_cleaned_lst_mean[1][lenth[2]:lenth[3]], label=display2, color='red')
	axs[1,1].errorbar(lable1[lenth[2]:lenth[3]], two_cleaned_lst_mean[1][lenth[2]:lenth[3]], two_cleaned_lst[1][lenth[2]:lenth[3]],
							fmt='o', ecolor='red', elinewidth=2, capsize=5)
	if len(data_fold1) > 2:

		axs[1,1].plot(lable1[lenth[2]:lenth[3]], two_cleaned_lst_mean[2][lenth[2]:lenth[3]], label=display3, color='green')
		axs[1,1].errorbar(lable1[lenth[2]:lenth[3]], two_cleaned_lst_mean[2][lenth[2]:lenth[3]], two_cleaned_lst[2][lenth[2]:lenth[3]],
								fmt='o', ecolor='green', elinewidth=2, capsize=5)

		axs[1,1].plot(lable1[lenth[2]:lenth[3]], two_cleaned_lst_mean[3][lenth[2]:lenth[3]], label=display4, color='black')
		axs[1,1].errorbar(lable1[lenth[2]:lenth[3]], two_cleaned_lst_mean[3][lenth[2]:lenth[3]], two_cleaned_lst[3][lenth[2]:lenth[3]],
								fmt='o', ecolor='black', elinewidth=2, capsize=5)


	#print(lenth)
	#print(lable1)
	for i in range(int(len(lable1)/2)):  #range(len(lable1)) 使用 range(len(x)) 确保不会超出索引范围

		list_data=[two_cleaned_lst_mean[0][i],two_cleaned_lst_mean[1][i],two_cleaned_lst_mean[2][i],two_cleaned_lst_mean[3][i]]



		if i <lenth[0]:
			axs[0,0].text(lable1[i]+1, two_cleaned_lst_mean[0][i],f'{two_cleaned_lst_mean[0][i]:.5f} ± {two_cleaned_lst[0][i]:.5f}', ha='right', va='bottom',color='blue')
			# fig = axs[0,0].figure
			# dpi = fig.dpi
			# offset = transforms.ScaledTranslation(0,0.5/2.54, fig.dpi_scale_trans)  # 1cm = 1/2.54英寸
			# trans = axs[0,0].transData + offset

			axs[0,0].text(lable1[i] + 1, two_cleaned_lst_mean[1][i], f'{two_cleaned_lst_mean[1][i]:.5f} ± {two_cleaned_lst[1][i]:.5f}', ha='right',
						va='bottom',color='red')

			if len(data_fold1) > 2:

				# fig = axs[0,0].figure
				# dpi = fig.dpi
				# offset = transforms.ScaledTranslation(0, 1 / 2.54, fig.dpi_scale_trans)  # 1cm = 1/2.54英寸
				# trans = axs[0,0].transData + offset

				axs[0,0].text(lable1[i] + 1, two_cleaned_lst_mean[2][i],
							f'{two_cleaned_lst_mean[2][i]:.5f} ± {two_cleaned_lst[2][i]:.5f}', ha='right',
							va='bottom', color='green')

				# fig = axs[0,0].figure
				# dpi = fig.dpi
				# offset = transforms.ScaledTranslation(0, -1 / 2.54, fig.dpi_scale_trans)  # 1cm = 1/2.54英寸
				# trans = axs[0,0].transData + offset

				axs[0,0].text(lable1[i] + 1, two_cleaned_lst_mean[3][i],
							f'{two_cleaned_lst_mean[3][i]:.5f} ± {two_cleaned_lst[3][i]:.5f}', ha='right',
							va='bottom', color='black')

		if lenth[0]<= i <lenth[1]:

			axs[0,1].text(lable1[i]+1, two_cleaned_lst_mean[0][i], f'{two_cleaned_lst_mean[0][i]:.5f} ± {two_cleaned_lst[0][i]:.5f}', ha='right',va='bottom',color='blue')
			#
			# fig = axs[0,1].figure
			# dpi = fig.dpi
			# offset = transforms.ScaledTranslation(0,0.5/2.54, fig.dpi_scale_trans)  # 1cm = 1/2.54英寸
			# trans = axs[0,1].transData + offset
			axs[0,1].text(lable1[i] + 1, two_cleaned_lst_mean[1][i], f'{two_cleaned_lst_mean[1][i]:.5f} ± {two_cleaned_lst[1][i]:.5f}', ha='right',
						va='bottom',color='red')

			if len(data_fold1) > 2:
				# fig = axs[0,1].figure
				# dpi = fig.dpi
				# offset = transforms.ScaledTranslation(0, 1 / 2.54, fig.dpi_scale_trans)  # 1cm = 1/2.54英寸
				# trans = axs[0,1].transData + offset
				axs[0,1].text(lable1[i] + 1, two_cleaned_lst_mean[2][i],
							f'{two_cleaned_lst_mean[2][i]:.5f} ± {two_cleaned_lst[2][i]:.5f}', ha='right',
							va='bottom', color='green')


				# fig = axs[0,1].figure
				# dpi = fig.dpi
				# offset = transforms.ScaledTranslation(0, -1 / 2.54, fig.dpi_scale_trans)  # 1cm = 1/2.54英寸
				# trans = axs[0,1].transData + offset
				axs[0,1].text(lable1[i] + 1, two_cleaned_lst_mean[3][i],
							f'{two_cleaned_lst_mean[3][i]:.5f} ± {two_cleaned_lst[3][i]:.5f}', ha='right',
							va='bottom', color='black')


		if lenth[1] <= i <lenth[2]:

			axs[1,0].text(lable1[i]+1, two_cleaned_lst_mean[0][i], f'{two_cleaned_lst_mean[0][i]:.5f} ± {two_cleaned_lst[0][i]:.5f}', ha='right',va='bottom',color='blue')
			#
			# fig = axs[1,0].figure
			# dpi = fig.dpi
			# offset = transforms.ScaledTranslation(0,0.5/2.54, fig.dpi_scale_trans)  # 1cm = 1/2.54英寸
			# trans = axs[1,0].transData + offset
			axs[1,0].text(lable1[i] + 1, two_cleaned_lst_mean[1][i], f'{two_cleaned_lst_mean[1][i]:.5f} ± {two_cleaned_lst[1][i]:.5f}', ha='right',
						va='bottom',color='red')
			if len(data_fold1) > 2:

				# fig = axs[1,0].figure
				# dpi = fig.dpi
				# offset = transforms.ScaledTranslation(0,1/2.54, fig.dpi_scale_trans)  # 1cm = 1/2.54英寸
				# trans = axs[1,0].transData + offset
				axs[1,0].text(lable1[i] + 1, two_cleaned_lst_mean[2][i], f'{two_cleaned_lst_mean[2][i]:.5f} ± {two_cleaned_lst[2][i]:.5f}', ha='right',
							va='bottom',color='green')

				# fig = axs[1,0].figure
				# dpi = fig.dpi
				# offset = transforms.ScaledTranslation(0,-1/2.54, fig.dpi_scale_trans)  # 1cm = 1/2.54英寸
				# trans = axs[1,0].transData + offset
				axs[1,0].text(lable1[i] + 1, two_cleaned_lst_mean[3][i], f'{two_cleaned_lst_mean[3][i]:.5f} ± {two_cleaned_lst[3][i]:.5f}', ha='right',
							va='bottom',color='black')

		if lenth[2] <= i <lenth[3]:

			axs[1,1].text(lable1[i]+1, two_cleaned_lst_mean[0][i], f'{two_cleaned_lst_mean[0][i]:.5f} ± {two_cleaned_lst[0][i]:.5f}', ha='right',va='bottom',color='blue')

			# fig = axs[1,1].figure
			# dpi = fig.dpi
			# offset = transforms.ScaledTranslation(0, 0.5/2.54, fig.dpi_scale_trans)  # 1cm = 1/2.54英寸
			# trans = axs[1,1].transData + offset
			axs[1,1].text(lable1[i] + 1, two_cleaned_lst_mean[1][i], f'{two_cleaned_lst_mean[1][i]:.5f} ± {two_cleaned_lst[1][i]:.5f}', ha='right',
						va='bottom',color='red')

			if len(data_fold1) > 2:

				# fig = axs[1,1].figure
				# dpi = fig.dpi
				# offset = transforms.ScaledTranslation(0, 1 / 2.54, fig.dpi_scale_trans)  # 1cm = 1/2.54英寸
				# trans = axs[1,1].transData + offset
				axs[1,1].text(lable1[i] + 1, two_cleaned_lst_mean[2][i],
							f'{two_cleaned_lst_mean[2][i]:.5f} ± {two_cleaned_lst[2][i]:.5f}', ha='right',
							va='bottom', color='green')


				# fig = axs[1,1].figure
				# dpi = fig.dpi
				# offset = transforms.ScaledTranslation(0, -1 / 2.54, fig.dpi_scale_trans)  # 1cm = 1/2.54英寸
				# trans = axs[1,1].transData + offset
				axs[1,1].text(lable1[i] + 1, two_cleaned_lst_mean[3][i],
							f'{two_cleaned_lst_mean[3][i]:.5f} ± {two_cleaned_lst[3][i]:.5f}', ha='right',
							va='bottom', color='black')


	#print(f'{cleaned_lst[i]:.6f} ± {cleaned_lst_mean[i]:.6f}')
	#显示图表
	axs[0,0].set_title("0号楼")
	axs[0,0].set_xlabel("测试距离m")
	axs[0,0].set_ylabel("测试误差m")
	axs[0,0].set_ylim(-0.02, 0.06)
	axs[0,0].set_xlim(0,50)
	axs[0,0].legend()

	axs[0,1].set_title("1楼")
	axs[0,1].set_xlabel("测试距离m")
	axs[0,1].set_ylabel("测试误差m")
	axs[0,1].set_ylim(-0.02, 0.06)
	axs[0,1].set_xlim(0,50)
	axs[0,1].legend()


	axs[1,0].set_title("创新大厦2楼平台")
	axs[1,0].set_xlabel("测试距离m")
	axs[1,0].set_ylabel("测试误差m")
	axs[1,0].set_ylim(-0.02, 0.06)
	axs[1,0].set_xlim(0,50)
	axs[1,0].legend()

	axs[1,1].set_title("眷诚斋")
	axs[1,1].set_xlabel("测试距离m")
	axs[1,1].set_ylabel("测试误差m")
	axs[1,1].set_ylim(-0.02, 0.06)
	axs[1,1].set_xlim(0,50)
	axs[1,1].legend()


	plt.show()


if __name__=="__main__":
	data_fold = r"G:\TK-set\2.1data\20251110-2device-360\CF52\对比"
	lable_display1="360全站仪回归第一侧"
	lable_display2 = "360全站仪回归另一侧"
	lable_display3 = "360全站仪回归两侧"
	lable_display4 = "180度全站仪回归标定"

	two_devie(lable_display1,lable_display2,lable_display3,lable_display4,data_fold)
