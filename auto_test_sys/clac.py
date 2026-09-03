#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2023/2/16 17:33
# @Author  : bhb
# @Email   : 
# @File    : clac.py

#标定相机
from PyQt5.QtCore import Qt, QThread, pyqtSignal

import glob

import cv2
import numpy as np
from PIL import Image
import time



class ClacThread(QThread):
    my_signal = pyqtSignal(str)
    my_signal_1 = pyqtSignal(str)

    def __init__(self,dir_path=""):
        super(ClacThread, self).__init__()
        self.dir_path=dir_path


    def run(self):
        self.clac_Matrix(self.dir_path)


    def clac_Matrix(self,dir_path):
        '''
        标定相机的内参矩阵
        :param dir_path:
        :return:
        '''
        try:
            # 8行11列棋盘角点
            CHECKERBOARD = (8, 6)
            criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 50, 0.001)

            # 世界坐标中的3D角点，z恒为0
            objpoints = []
            # 像素坐标中的2D点
            imgpoints = []

            # 利用棋盘定义世界坐标系中的角点
            objp = np.zeros((1, CHECKERBOARD[0] * CHECKERBOARD[1], 3), np.float32)
            objp[0, :, :2] = np.mgrid[0:CHECKERBOARD[0], 0:CHECKERBOARD[1]].T.reshape(-1, 2)

            # 从文件夹中读取所有图片
            images = glob.glob(dir_path+'\*.jpg')
            if len(images)==0:
                self.my_signal.emit(time.strftime("%Y-%m-%d %H:%M:%S    ") + "【WARNING】文件夹内没有找到图片！")
                self.my_signal_1.emit(";")
                return None
            gray = None
            for i in range(len(images)):
                fname = images[i]
                print(images[i])
                self.my_signal.emit(time.strftime("%Y-%m-%d %H:%M:%S    ")+"当前处理"+fname)
                img = cv2.imread(fname)#cv2.imdecode(np.fromfile(fname), cv2.IMREAD_UNCHANGED)##会读成长>宽
                gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
                # 查找棋盘角点
                ret, corners = cv2.findChessboardCorners(gray, CHECKERBOARD, cv2.CALIB_CB_ADAPTIVE_THRESH +
                                                         cv2.CALIB_CB_FAST_CHECK + cv2.CALIB_CB_NORMALIZE_IMAGE)
                """
                使用cornerSubPix优化探测到的角点
                """
                if ret == True:
                    objpoints.append(objp)
                    corners2 = cv2.cornerSubPix(gray, corners, (11, 11), (-1, -1), criteria)
                    imgpoints.append(corners2)
                    # 显示角点
                    img = cv2.drawChessboardCorners(img, CHECKERBOARD, corners2, ret)
                    new_img = Image.fromarray(img.astype(np.uint8))
                    new_img.save('chessboard_{}.png'.format(i))
                    print('chessboard_{}.png'.format(i))
                    # plt.imshow(img)
                    # plt.show()
                # cv2.imshow('img', img)
                # cv2.waitKey(0)

            # cv2.destroyAllWindows()
            # 标定
            ret, mtx, dist, rvecs, tvecs = cv2.calibrateCamera(objpoints, imgpoints, gray.shape[::-1], None, None)
            print("旋转向量 : \n")
            print(rvecs)
            print("平移向量 : \n")
            print(tvecs)

            print("内参 : \n")
            print(mtx)
            print("畸变 : \n")
            print(dist)

            self.my_signal.emit(time.strftime("%Y-%m-%d %H:%M:%S    ") + "重投影误差:" + str(ret))
            out_str=""
            rows, cols = mtx.shape  # 获取矩阵的行数和列数
            for i in range(rows):  # 按照行来遍历
                for j in range(cols):  # 对第i行进行遍历
                    out_str+="%.4f" % mtx[i, j]
                    out_str+=" "
                out_str += "\n"
            out_str=out_str[:-1]+";"
            for item in dist[0][:-1]:#只要4个即可
                out_str += "%.4f" % item
                out_str += " "
            self.my_signal_1.emit(out_str)
        except Exception as e:
            self.my_signal.emit(time.strftime("%Y-%m-%d %H:%M:%S    ") + "出现错误:" + str(e))



#print(np.arctan(0.005/10)/np.pi*180)

#C7DF3046210E相机 内参（B1样机朝前）
#[[3.31872555e+03 0.00000000e+00 1.56873082e+03]
 #[0.00000000e+00 3.32365653e+03 2.44411762e+03]
 #[0.00000000e+00 0.00000000e+00 1.00000000e+00]]
#畸变 :

#[[ 0.00092066  0.08492354 -0.00079536 -0.00198893 -0.18864905]]



#C7DF304625AA相机 内参（B1样机朝上）
#[[3.30687327e+03 0.00000000e+00 1.56696084e+03]
# [0.00000000e+00 3.30920320e+03 2.43009739e+03]
# [0.00000000e+00 0.00000000e+00 1.00000000e+00]]
#畸变 :

#[[-0.01294558  0.15556114  0.0015029  -0.00383836 -0.44448507]]

# c=ClacThread()
# c.clac_Matrix(r"C:\Users\bhb\Desktop\tttt")
#
#
# camera_matrix = np.array([[3.42088774e+03,0.00000000e+00,1.58106919e+03],
#  [0.00000000e+00,3.42344968e+03,2.75414056e+03],
#  [0.00000000e+00,0.00000000e+00,1.00000000e+00]], dtype=np.float32)
# #
# # # 定义畸变系数
# # # 这里使用示例值，实际使用时需要根据具体相机进行标定
# dist_coeffs = np.array([1.81877588e-01,-7.91280054e-01,-6.44243502e-04,1.76936147e-03,8.15569397e-01], dtype=np.float32)
#
# # camera_matrix = np.array([[2.10829518e+03,0.00000000e+00,2.05761754e+03],
# #                           [0, 2.10584037e+03,1.49778728e+03],
# #                           [0, 0, 1]], dtype=np.float32)
# # print(np.arctan(7.4/2/3.37)*2/np.pi*180)
# #
hv=np.arctan((4800/2)/3332)*2
print("hv:",hv/np.pi*180)
# v_view=np.arctan((3072/2)/3482)*2
# print("v_view:",v_view/np.pi*180)
#
#
# #定义畸变系数
# #这里使用示例值，实际使用时需要根据具体相机进行标定
# # dist_coeffs = np.array([-0.15866041,0.10163431,-0.00016078,0.0003429,-0.0328828 ], dtype=np.float32)
# #
# 读取图像
# img = cv2.imread(r'C:\Users\bhb\Desktop\2025-09-02_16-37-46\2-1.jpg')
# # 获取图像尺寸
# h, w = img.shape[:2]
#
# # 优化相机矩阵
# new_camera_matrix, roi = cv2.getOptimalNewCameraMatrix(camera_matrix, dist_coeffs, (w, h), 1, (w, h))
#
# # 进行畸变矫正
# dst = cv2.undistort(img, camera_matrix, dist_coeffs, None, new_camera_matrix)
# x, y, w, h = roi
# cv2.rectangle(dst,roi,(0,0,255),2)
# #dst = dst[y:y+h, x:x+w]
# cv2.imwrite("test.jpg",dst)
# print("裁剪后的水平视野",w/dst.shape[1]*hv/np.pi*180)
# print("裁剪后的垂直视野",h/dst.shape[0]*v_view/np.pi*180)