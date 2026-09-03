import skspatial.objects as sko
import numpy as np
import open3d as o3d
import matplotlib.pyplot as plt
#文件夹路径
fold1=r"C:\Users\ZHXR\Desktop\com_tool\2.1data\testbd\全站仪数据\compare\0号楼/"
fold2=r"C:\Users\ZHXR\Desktop\com_tool\2.1data\testbd\全站仪数据\compare\创新大厦2楼平台/"
fold3=r"C:\Users\ZHXR\Desktop\com_tool\2.1data\testbd\全站仪数据\compare\1楼/"
fold4=r"C:\Users\ZHXR\Desktop\com_tool\2.1data\testbd\全站仪数据\compare\眷诚斋/"
folds =[fold1,fold2,fold3,fold4]
#fold = r"C:\Users\ZHXR\Desktop\2.1data\testbd\全站仪数据\compare\0号楼/" #件夹路径
knn_n= 32 #计算点个数（如coludecomare 计算时的6points
points_TS_str=0   #1是第一列为非数据 0是直接第一列为数据
TS_files=[]
#TS_files =['四周','高处','楼顶部','地面']
TS_file1 =['四周','高处','楼顶部','地面']
TS_file2 =['地面','高程顶盖','水池','右立面1','右立面2','会堂','科技大厦']
TS_file3 =['1号墙壁','2号墙壁','3号墙壁','4号墙壁','创新1号面','创新2号面','创新高程顶部']
#TS_file3 =['1号墙壁','2号墙壁','3号墙壁','4号墙壁','创新1号面','创新2号面']
TS_file4 =['地面','1-1','1-2','1-3','1-4','2-1','2-2','3-1','4-1']
dict_dist={}

PC_file='AllGeoPoints.txt'
for id,fold in enumerate(folds):
	if fold == folds[0]:
		#continue
		TS_files=TS_file1

		print("0号楼")
	elif fold == folds[1]:
		#continue
		TS_files = TS_file2

		print("创新大厦2楼平台")
	elif fold == folds[2]:
		#continue
		TS_files = TS_file3
		print("1楼")

	else :
		#continue
		TS_files = TS_file4

		print("眷诚斋")

	dict_dist[str(id)] = {}
	points_PC = np.loadtxt(fold + PC_file)[:, 0:3]   #读取完整点云AllGeoPoints.txt,返回NumPy数组，包含了所有点的三维坐标
	pc_PC = o3d.geometry.PointCloud()  # type:open3d.cpu.pybind.geometry.PointCloud #创建一个空的open3d的点云对象
	pc_PC.points = o3d.utility.Vector3dVector(points_PC)  #设置点云对象的点
	pcd_tree = o3d.geometry.KDTreeFlann(pc_PC)  #为点云对象创建KD树：KD树是一种数据结构
	#用于在多维空间中组织点，以便进行有效的搜索操作，如最近邻搜索
	points_TS_all=np.empty([0,4])
	for TS_file in TS_files:                              #读取截取的点云（全站仪打点）
		if points_TS_str:
			points_TS_str = np.loadtxt(fold + TS_file+'.txt', dtype=str, delimiter=',')
			ind = np.where(points_TS_str[:, 1] != '')[0] #返回是一维数组[0 1 2 3 ...99]第二列不为0的索引行号
			points_TS = np.ones([len(ind), 4])
			points_TS[:, 0:3] = points_TS_str[ind, 1:4].astype(float)  #将算中的数据块转化为浮点数
		else:
			points_TS= np.loadtxt(fold + TS_file+'.txt')[:, 0:3]
			points_TS = np.ones([len(points_TS[:,1]), 4])
			points_TS[:, 0:3] = np.loadtxt(fold + TS_file+'.txt')[:, 0:3]

		points_v_out = []
		#print(len(points_TS))
		for i in range(len(points_TS)):
			[_, ind, _] = pcd_tree.search_knn_vector_3d(points_TS[i,0:3], knn_n)
			neibr_points = np.asarray(pc_PC.points)[ind]
			try:
				plane = sko.Plane.best_fit(neibr_points)
				v = plane.distance_point_signed(points_TS[i, 0:3])
				points_v_out.append(v)
			except Exception as e:
				# print(e)
				pass
		points_v_out = np.array(points_v_out)
		# if len(points_TS)>len(points_v_out):
		# 	print(f"输入点数为{len(points_TS)}，参与计算的点个数为{len(points_v_out)}")

		scan_dist=np.linalg.norm(points_TS[:,0:3],axis=1).mean()
		points_TS_all=np.append(points_TS_all,points_TS)

		name=TS_file+f"-{str(round(scan_dist,1))}m"
		data_mean=np.mean(np.abs(points_v_out))
		data_std=np.std(np.abs(points_v_out))

		dict_dist[str(id)][name]=[data_mean,data_std]
# print(dict_dist)
# print(len(dict_dist))
fig,axs=plt.subplots(2,2,figsize=(10,5))
plt.tight_layout()
plt.rcParams['font.sans-serif'] = ['SimHei']  # 指定默认字体
plt.rcParams['axes.unicode_minus'] = False

dict_names=list(dict_dist.keys())
for i,dict_name in enumerate(dict_names):
	dict_location=list(dict_dist[dict_name].keys())
	print(dict_location)
	dict_value=list(dict_dist[dict_name].values())
	dict_value=np.array(dict_value)
	print(dict_value)
	if i==1:
		axs[0,0].plot(dict_location,dict_value[:,0],label='0号楼',color='blue')
		axs[0,0].legend(loc='upper right')
		axs[0, 0].errorbar(dict_location,dict_value[:,0],dict_value[:,1],
						   fmt='o',ecolor='blue', elinewidth=2, capsize=5, color='blue')
	if i==2:
		axs[0,1].plot(dict_location,dict_value[:,0],label='1楼',color='red')
		axs[0,1].legend(loc='upper right')
		axs[0,1].errorbar(dict_location, dict_value[:, 0], dict_value[:, 1],
						   fmt='o', ecolor='red', elinewidth=2, capsize=5, color='red')

	if i==3:
		axs[1,0].plot(dict_location,dict_value[:,0],label='2楼',color='green')
		axs[1,0].legend(loc='upper right')
		axs[1,0].errorbar(dict_location, dict_value[:, 0], dict_value[:, 1],
						   fmt='o', ecolor='green', elinewidth=2, capsize=5, color='green')
	if i==4:
		axs[1,1].plot(dict_location,dict_value[:,0],label='宿舍',color='black')
		axs[1,1].legend(loc='upper right')
		axs[1,1].errorbar(dict_location, dict_value[:, 0], dict_value[:, 1],
						   fmt='o', ecolor='black', elinewidth=2, capsize=5, color='black')
plt.show()



# axs[0,0].set_title("0号楼")
# axs[0, 0].set_xlabel("测试距离m")
# axs[0, 0].set_ylabel("测试误差m")
# axs[0, 0].set_ylim(-0.02, 0.05)
# axs[0, 0].set_xlim(0, 50)
# axs[0, 0].legend(loc='upper right')
# axs[0, 1].set_title("1楼")
# axs[0, 1].set_xlabel("测试距离m")
# axs[0, 1].set_ylabel("测试误差m")
# axs[0, 1].set_ylim(-0.02, 0.1)
# axs[0, 1].set_xlim(0, 50)
# axs[0, 1].legend(loc='upper right')
# axs[1,0].set_title("0号楼")
# axs[1,0].set_xlabel("测试距离m")
# axs[1,0].set_ylabel("测试误差m")
# axs[1,0].set_ylim(-0.02, 0.05)
# axs[1,0].set_xlim(0, 50)
# axs[1,0].legend(loc='upper right')
# axs[1, 1].set_title("1楼")
# axs[1, 1].set_xlabel("测试距离m")
# axs[1, 1].set_ylabel("测试误差m")
# axs[1, 1].set_ylim(-0.02, 0.1)
# axs[1, 1].set_xlim(0, 50)
# axs[1, 1]].legend(loc='upper right')



	# 	print(TS_file+'('+str(round(scan_dist,1))+')最大绝对距离：'+str(np.abs(points_v_out).max())+';平均距离（位置精度）：'+str(np.mean(np.abs(points_v_out)))+';标准差(点云厚度)：'+ str(np.std(np.abs(points_v_out))))#points_TS[:,3]
	# np.savetxt(fold+'TStoPCdist.txt',points_TS_all,'%.04f')
