from PyQt5.QtCore import Qt, QThread, pyqtSignal
import skspatial.objects as sko
import numpy as np
import open3d as o3d
import os
import time

class ClacTestThread(QThread):
    my_signal = pyqtSignal(str)
    my_signal_1 = pyqtSignal(str)

    def __init__(self,path0,path1):
        super(ClacTestThread, self).__init__()
        self.path0=path0
        self.path1 = path1


    def run(self):
        return self.run_exe(self.path0,self.path1)

    def run_exe(self,txt_path,dir_path):
        try:
            knn_n = 30  # 计算点个数（如coludecomare 计算时的6points
            start_time = time.time()
            points_PC = np.loadtxt(txt_path)[:, 0:3]
            time_str = f"加载{os.path.basename(txt_path)}   耗时: {time.time() - start_time} s"
            #self.my_signal.emit(time_str)

            pc_PC = o3d.geometry.PointCloud()  # type:open3d.cpu.pybind.geometry.PointCloud
            pc_PC.points = o3d.utility.Vector3dVector(points_PC)
            pcd_tree = o3d.geometry.KDTreeFlann(pc_PC)
            a=[]
            out_strs=[]
            points_TS_all = np.empty([0, 4])
            for path in os.listdir(dir_path):
                if path[-4:] == ".txt":
                    t_path = os.path.join(dir_path, path)
                    points_TS = np.loadtxt(t_path)[:, 0:3]
                    points_TS = np.ones([len(points_TS[:, 1]), 4])
                    points_TS[:, 0:3] = np.loadtxt(t_path)[:, 0:3]

                    for i in range(len(points_TS)):
                        [_, ind, _] = pcd_tree.search_knn_vector_3d(points_TS[i, 0:3], knn_n)
                        neibr_points = np.asarray(pc_PC.points)[ind]
                        try:
                            plane = sko.Plane.best_fit(neibr_points)
                            points_TS[i, 3] = plane.distance_point_signed(points_TS[i, 0:3])

                        except Exception as e:
                            # print(e)
                            pass
                    #print(f"points_TS:{points_TS}")



                    # print(type(points_TS))
                    scan_dist = np.linalg.norm(points_TS[:, 0:3], axis=1).mean()
                    points_TS_all = np.append(points_TS_all, points_TS)
                    a.extend(points_TS[:, 3])

                    out_str = path + '(' + str(round(scan_dist, 1)) + ')最大绝对距离：' + str(
                        round(np.abs(points_TS[:, 3]).max(),4)) + ';平均距离：' + str(round(points_TS[:, 3].mean(),4)) + ';标准差：' + str(round(
                        points_TS[:, 3].std(),4))
                    out_strs.append(out_str)
                    #print(out_strs)
                    #self.my_signal.emit(out_str)
            #self.my_signal_1.emit("计算完成")  # 返回结果
            return out_strs
        except Exception as e:
            print(e)
        #     #self.my_signal.emit(e)
        #     #self.my_signal_1.emit("计算完成")  # 返回结果

