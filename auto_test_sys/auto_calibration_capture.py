#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
自动相机内参标定数据采集脚本
功能：控制机械臂到指定角度并拍摄照片，用于相机内参标定
"""

import time
import sys
import os
from datetime import datetime
import argparse

import glob
import cv2
import numpy as np


# 导入机械臂控制模块
try:
    from controller import set_servo_angle, current_angles
except ImportError:
    print("错误：无法导入controller模块，请确保controller.py在同一目录下")
    sys.exit(1)

# 导入相机控制模块
try:
    from testcamera import set_resolution, capture_image, is_image_valid
except ImportError:
    print("错误：无法导入testcamera模块，请确保testcamera.py在同一目录下")
    sys.exit(1)

class CalibrationDataCollector:
    """相机内参标定数据采集器"""
    
    def __init__(self, camera_device="/dev/video0", output_dir="calibration_data"):
        self.camera_device = camera_device
        self.output_dir = output_dir
        self.resolution_width = 5472  # 16M分辨率宽度
        self.resolution_height = 3078  # 16M分辨率高度
        self.angle_data_file = "77采集.txt"
        self.setup_directories()
        
    def setup_directories(self):
        """创建必要的目录"""
        # 检查主输出目录是否存在
        if os.path.exists(self.output_dir):
            print(f"警告：输出目录已存在: {self.output_dir}")
            choice = input("是否删除现有目录并继续？(y/N): ").strip().lower()
            if choice == 'y' or choice == 'yes':
                try:
                    import shutil
                    shutil.rmtree(self.output_dir)
                    print(f"已删除目录: {self.output_dir}")
                except Exception as e:
                    print(f"删除目录失败: {e}")
                    sys.exit(1)
            else:
                print("用户取消操作，程序退出")
                sys.exit(1)
        
        # 创建主输出目录
        os.makedirs(self.output_dir)
        print(f"创建输出目录: {self.output_dir}")
        
        # 创建子目录用于存储不同角度的照片
        self.images_dir = os.path.join(self.output_dir, "images")
        self.logs_dir = os.path.join(self.output_dir, "logs")
        
        for directory in [self.images_dir, self.logs_dir]:
            os.makedirs(directory)
                
    def setup_camera(self):
        """设置相机参数"""
        print("正在设置相机分辨率...")
        try:
            set_resolution(self.camera_device, self.resolution_width, self.resolution_height)
            print(f"相机分辨率已设置为: {self.resolution_width}x{self.resolution_height}")
            time.sleep(2)  # 等待设置生效
            return True
        except Exception as e:
            print(f"设置相机分辨率失败: {e}")
            return False
            
    def read_angle_data(self):
        """读取角度数据文件"""
        try:
            with open(self.angle_data_file, 'r', encoding='utf-8') as f:
                lines = f.readlines()
            
            angle_sets = []
            for line_num, line in enumerate(lines, 1):
                line = line.strip()
                if line:  # 跳过空行
                    try:
                        angles = [float(x) for x in line.split()]
                        if len(angles) == 6:  # 确保有6个角度值
                            angle_sets.append({
                                'line_number': line_num,
                                'angles': angles
                            })
                        else:
                            print(f"警告：第{line_num}行角度数量不正确，跳过")
                    except ValueError:
                        print(f"警告：第{line_num}行数据格式错误，跳过")
            
            print(f"成功读取 {len(angle_sets)} 组角度数据")
            return angle_sets
            
        except FileNotFoundError:
            print(f"错误：找不到角度数据文件 {self.angle_data_file}")
            return []
        except Exception as e:
            print(f"读取角度数据文件失败: {e}")
            return []
            
    def move_arm_to_angles(self, angles, delay=5):
        """移动机械臂到指定角度"""
        print(f"正在移动机械臂到角度: {angles}")
        
        # 依次设置每个通道的角度
        for channel, angle in enumerate(angles[:6]):  # 只使用前6个角度
            try:
                success = set_servo_angle(channel, angle,False)
                if not success:
                    print(f"警告：设置通道{channel}角度{angle}失败")
                time.sleep(0.5)  # 短暂延迟避免通信冲突
            except Exception as e:
                print(f"错误：设置通道{channel}时发生异常: {e}")
                return False
        
        print("机械臂移动完成，等待稳定...")
        time.sleep(delay)  # 等待机械臂稳定
        return True
        
    def capture_photo(self, photo_index):
        """拍摄照片"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"calib_{photo_index:03d}_{timestamp}.jpg"
        filepath = os.path.join(self.images_dir, filename)
        
        print(f"正在拍摄照片: {filename}")
        
        try:
            # 最多尝试5次采集
            max_attempts = 5
            for attempt in range(max_attempts):
                try:
                    capture_image(self.camera_device, filepath)
                    time.sleep(2)
                    # 验证照片是否有效
                    if is_image_valid(filepath):
                        print(f"✓ 照片拍摄成功: {filename}")
                        return filepath
                    else:
                        print(f"✗ 照片文件无效: {filename}")
                        # 删除无效文件
                        if os.path.exists(filepath):
                            os.remove(filepath)
                            print(f"已删除无效文件: {filename}")
                        
                        # 如果不是最后一次尝试，继续重试
                        if attempt < max_attempts - 1:
                            print(f"第{attempt + 1}次采集失败，正在重试...")
                            time.sleep(1)  # 短暂延迟后重试
                        else:
                            print(f"已达最大重试次数({max_attempts})，采集失败")
                            return None
                except Exception as e:
                    print(f"✗ 拍摄照片时发生异常: {e}")
                    # 删除可能创建的损坏文件
                    if os.path.exists(filepath):
                        os.remove(filepath)
                        print(f"已删除损坏文件: {filename}")
                    
                    if attempt < max_attempts - 1:
                        print(f"第{attempt + 1}次采集异常，正在重试...")
                        time.sleep(1)
                    else:
                        print(f"已达最大重试次数({max_attempts})，采集失败")
                        return None
                
        except Exception as e:
            print(f"✗ 拍摄照片失败: {e}")
            return None
            
    def log_capture_result(self, photo_index, angles, photo_path, success):
        """记录采集结果"""
        log_file = os.path.join(self.logs_dir, "capture_log.txt")
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        log_entry = f"[{timestamp}] 序号:{photo_index:03d} "
        log_entry += f"角度:[{', '.join(f'{a:.1f}' for a in angles)}] "
        log_entry += f"结果:{'成功' if success else '失败'} "
        if photo_path:
            log_entry += f"文件:{os.path.basename(photo_path)}"
        log_entry += "\n"
        
        try:
            with open(log_file, 'a', encoding='utf-8') as f:
                f.write(log_entry)
        except Exception as e:
            print(f"记录日志失败: {e}")
            
    def generate_report(self, total_count, success_count):
        """生成采集报告"""
        report_file = os.path.join(self.output_dir, "calibration_report.txt")
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        report_content = f"""
相机内参标定数据采集报告
========================
采集时间: {timestamp}
输出目录: {os.path.abspath(self.output_dir)}
图像目录: {os.path.abspath(self.images_dir)}
日志目录: {os.path.abspath(self.logs_dir)}

采集统计:
--------
总采集次数: {total_count}
成功次数: {success_count}
成功率: {(success_count/total_count*100):.1f}% ({success_count}/{total_count})

相机参数:
--------
设备: {self.camera_device}
分辨率: {self.resolution_width}x{self.resolution_height}

文件说明:
--------
- images/: 存放采集的标定图像
- logs/capture_log.txt: 详细的采集日志
- calibration_report.txt: 本次采集的统计报告

使用建议:
--------
1. 检查images目录下的图像质量
2. 查看logs/capture_log.txt确认每张图像的采集情况
3. 如需重新采集某些角度，可根据日志定位问题
        """.strip()
        
        try:
            with open(report_file, 'w', encoding='utf-8') as f:
                f.write(report_content)
            print(f"采集报告已生成: {report_file}")
        except Exception as e:
            print(f"生成报告失败: {e}")
            
    def calculate_camera_parameters(self):
        """计算相机内参矩阵和畸变系数"""
        try:
            # 8行11列棋盘角点 (根据clac.py中的设置)
            CHECKERBOARD = (8, 6)
            criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 50, 0.001)
            
            # 世界坐标中的3D角点，z恒为0
            objpoints = []
            # 像素坐标中的2D点
            imgpoints = []
            
            # 利用棋盘定义世界坐标系中的角点
            objp = np.zeros((1, CHECKERBOARD[0] * CHECKERBOARD[1], 3), np.float32)
            objp[0, :, :2] = np.mgrid[0:CHECKERBOARD[0], 0:CHECKERBOARD[1]].T.reshape(-1, 2)
            
            # 从images目录中读取所有jpg图片
            images = glob.glob(os.path.join(self.images_dir, '*.jpg'))
            if len(images) == 0:
                print("警告：images目录内没有找到图片！")
                return False
                
            print(f"找到 {len(images)} 张图片用于标定")
            gray = None
            
            # 处理每张图片
            for i, fname in enumerate(images):
                print(f"处理图片 {i+1}/{len(images)}: {os.path.basename(fname)}")
                img = cv2.imread(fname)
                if img is None:
                    print(f"警告：无法读取图片 {fname}")
                    continue
                    
                gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
                # 查找棋盘角点
                ret, corners = cv2.findChessboardCorners(
                    gray, CHECKERBOARD, 
                    cv2.CALIB_CB_ADAPTIVE_THRESH + cv2.CALIB_CB_FAST_CHECK + cv2.CALIB_CB_NORMALIZE_IMAGE
                )
                
                # 使用cornerSubPix优化探测到的角点
                if ret == True:
                    objpoints.append(objp)
                    corners2 = cv2.cornerSubPix(gray, corners, (11, 11), (-1, -1), criteria)
                    imgpoints.append(corners2)
                    
                    # 显示角点（可选，保存为文件）
                    img_with_corners = cv2.drawChessboardCorners(img, CHECKERBOARD, corners2, ret)
                    corner_img_path = os.path.join(self.images_dir, f'chessboard_corners_{i:03d}.png')
                    cv2.imwrite(corner_img_path, img_with_corners)
                    print(f"已保存角点检测结果: {os.path.basename(corner_img_path)}")
                else:
                    print(f"警告：在图片 {os.path.basename(fname)} 中未找到棋盘角点")
            
            if len(objpoints) == 0:
                print("错误：没有找到任何有效的棋盘角点")
                return False
                
            # 标定相机
            print("正在进行相机标定...")
            ret, mtx, dist, rvecs, tvecs = cv2.calibrateCamera(
                objpoints, imgpoints, gray.shape[::-1], None, None
            )
            
            print("\n标定结果:")
            print("旋转向量:")
            print(rvecs)
            print("平移向量:")
            print(tvecs)
            print("\n内参矩阵:")
            print(mtx)
            print("畸变系数:")
            print(dist)
            print(f"\n重投影误差: {ret}")
            
            # 保存内参到txt文件（与文件夹同名）
            folder_name = os.path.basename(os.path.normpath(self.output_dir))
            calibration_file = os.path.join(self.images_dir, f"{folder_name}.txt")
            
            # 格式化输出内容
            calibration_content = self.format_calibration_results(mtx, dist, ret, len(objpoints))
            
            with open(calibration_file, 'w', encoding='utf-8') as f:
                f.write(calibration_content)
            
            print(f"\n✓ 相机内参已保存到: {calibration_file}")
            return True
            
        except Exception as e:
            print(f"计算相机内参时发生错误: {e}")
            import traceback
            traceback.print_exc()
            return False
            
    def format_calibration_results(self, mtx, dist, reprojection_error, image_count):
        """格式化标定结果为文本"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        # 格式化内参矩阵
        matrix_str = ""
        rows, cols = mtx.shape
        for i in range(rows):
            for j in range(cols):
                matrix_str += f"{mtx[i, j]:.6f}"
                if j < cols - 1:
                    matrix_str += " "
            matrix_str += "\n"
        
        # 格式化畸变系数（只取前4个）
        distortion_str = ""
        for i, coeff in enumerate(dist[0][:4]):
            distortion_str += f"{coeff:.6f}"
            if i < 3:  # 前3个后面加空格
                distortion_str += " "
        
        content = f"""
相机内参标定结果
================
标定时间: {timestamp}
使用图片数量: {image_count} 张
重投影误差: {reprojection_error:.6f}

内参矩阵 (Intrinsic Matrix):
{matrix_str}
畸变系数 (Distortion Coefficients):
{distortion_str}

说明:
----
- 内参矩阵格式: [fx 0 cx; 0 fy cy; 0 0 1]
- 畸变系数顺序: k1 k2 p1 p2
- fx, fy: 焦距(像素)
- cx, cy: 主点坐标(像素)
- k1, k2: 径向畸变系数
- p1, p2: 切向畸变系数
        """.strip()
        
        return content
            
    def run_calibration_capture(self, start_from=1, max_count=None):
        """执行完整的标定数据采集流程"""
        print("=" * 60)
        print("相机内参标定数据自动采集系统")
        print("=" * 60)
        print(f"输出目录: {os.path.abspath(self.output_dir)}")
        print(f"相机设备: {self.camera_device}")
        print(f"分辨率: {self.resolution_width}x{self.resolution_height}")
        print("-" * 60)
        
        # 1. 设置相机
        if not self.setup_camera():
            print("相机设置失败，程序退出")
            return False
            
        # 2. 读取角度数据
        angle_sets = self.read_angle_data()
        if not angle_sets:
            print("无有效角度数据，程序退出")
            return False
            
        # 3. 确定采集范围
        total_sets = len(angle_sets)
        if max_count:
            total_sets = min(max_count, total_sets)
            
        start_index = max(0, start_from - 1)
        end_index = min(start_index + total_sets, len(angle_sets))
        
        print(f"计划采集: 第{start_from}组到第{end_index}组，共{end_index - start_index}组")
        print("-" * 60)
        
        # 4. 开始采集
        success_count = 0
        processed_count = 0
        
        try:
            for i in range(start_index, end_index):
                angle_set = angle_sets[i]
                photo_index = i + 1
                angles = angle_set['angles']
                
                print(f"\n[{processed_count + 1}/{end_index - start_index}] 采集第{photo_index}组数据")
                print(f"目标角度: [{', '.join(f'{a:.1f}' for a in angles)}]")
                
                # 移动机械臂
                if not self.move_arm_to_angles(angles):
                    print("机械臂移动失败，跳过此组")
                    self.log_capture_result(photo_index, angles, None, False)
                    continue
                
                # 拍摄照片
                photo_path = self.capture_photo(photo_index)
                
                # 记录结果
                success = photo_path is not None
                if success:
                    success_count += 1
                    
                self.log_capture_result(photo_index, angles, photo_path, success)
                processed_count += 1
                
                # 进度提示
                if processed_count % 5 == 0:
                    progress = (processed_count / (end_index - start_index)) * 100
                    print(f"进度: {progress:.1f}% ({processed_count}/{end_index - start_index})")
                    
        except KeyboardInterrupt:
            print("\n\n用户中断采集过程")
        except Exception as e:
            print(f"\n采集过程中发生错误: {e}")
            
        # 5. 生成报告
        print("\n" + "=" * 60)
        print("采集完成!")
        print("=" * 60)
        print(f"总计处理: {processed_count} 组")
        print(f"成功采集: {success_count} 组")
        print(f"成功率: {(success_count/processed_count*100):.1f}%")
        print("-" * 60)
        
        self.generate_report(processed_count, success_count)
        
        # 6. 计算相机内参
        if success_count > 0:
            print("\n" + "=" * 60)
            print("开始计算相机内参...")
            print("=" * 60)
            calibration_success = self.calculate_camera_parameters()
            if calibration_success:
                print("✓ 相机内参计算完成")
            else:
                print("✗ 相机内参计算失败")
        
        return success_count > 0

def main():
    parser = argparse.ArgumentParser(description="相机内参标定数据自动采集")
    parser.add_argument("--output-dir", type=str, default="calibration_data",
                       help="输出数据目录 (默认: calibration_data)")
    parser.add_argument("--camera-device", type=str, default="/dev/video0",
                       help="相机设备路径 (默认: /dev/video0)")
    parser.add_argument("--start-from", type=int, default=1,
                       help="从第几组开始采集 (默认: 1)")
    parser.add_argument("--max-count", type=int,
                       help="最大采集组数 (默认: 全部)")
    parser.add_argument("--resolution", type=str, default="16M",
                       choices=['12M', '16M', '8M', '4K', '1080p'],
                       help="相机分辨率 (默认: 16M)")
    
    args = parser.parse_args()
    
    # 根据分辨率选择宽高
    resolution_map = {
        '12M': (4000, 3000),
        '16M': (5472, 3078),
        '8M': (3264, 2448),
        '4K': (3840, 2160),
        '1080p': (1920, 1080)
    }
    
    collector = CalibrationDataCollector(
        camera_device=args.camera_device,
        output_dir=args.output_dir
    )
    
    # 更新分辨率设置
    if args.resolution in resolution_map:
        collector.resolution_width, collector.resolution_height = resolution_map[args.resolution]
        print(f"设置分辨率为: {args.resolution} ({collector.resolution_width}x{collector.resolution_height})")
    
    # 执行采集
    success = collector.run_calibration_capture(
        start_from=args.start_from,
        max_count=args.max_count
    )
    
    if success:
        print(f"\n数据采集完成，请查看目录: {os.path.abspath(args.output_dir)}")
        sys.exit(0)
    else:
        print("\n数据采集失败")
        sys.exit(1)

if __name__ == "__main__":
    main()