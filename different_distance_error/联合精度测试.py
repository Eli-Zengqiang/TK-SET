import skspatial.objects as sko
import numpy as np
import open3d as o3d
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
TS_file4 =['地面','平面1','平面2','平面3','平面4','平面5','楼顶部','地面','水池','会堂']

PC_file='AllGeoPoints.txt'
for fold in folds:
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
		continue
		TS_files = TS_file4

		print("象印")



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
		print(TS_file+'('+str(round(scan_dist,1))+'m)最大绝对距离：'+str(np.abs(points_v_out).max())+';平均距离（位置精度）：'+str(np.mean(np.abs(points_v_out)))+';标准差(点云厚度)：'+ str(np.std(np.abs(points_v_out))))#points_TS[:,3]
	np.savetxt(fold+'TStoPCdist.txt',points_TS_all,'%.04f')