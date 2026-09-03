#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
功能：为全站仪坐标文件中的每个点，在点云文件中找到最近的点
说明：只处理每个文件的前三列（x y z），忽略其他所有列
输入：全站仪坐标文件(x y z ...)，点云坐标文件(x y z ...)
输出：最近点坐标文件(x y z)，顺序与全站仪文件对应
"""

import numpy as np
from scipy.spatial import KDTree
import sys
import os

def read_xyz_only(filepath, description):
    """
    只读取文件的前三列（x, y, z坐标）
    完全忽略第4列及以后的所有内容
    """
    print(f"\n正在读取{description}...")
    print(f"文件路径: {filepath}")
    
    if not os.path.exists(filepath):
        print(f"错误：文件不存在！")
        return None
    
    points = []
    line_count = 0
    error_count = 0
    
    try:
        with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
            for line_num, line in enumerate(f, 1):
                line = line.strip()
                
                # 跳过空行和注释行（以#开头）
                if not line or line.startswith('#'):
                    continue
                
                # 按空白字符分割（支持空格和制表符）
                parts = line.split()
                
                # 只取前三列
                if len(parts) >= 3:
                    try:
                        x = float(parts[0])
                        y = float(parts[1])
                        z = float(parts[2])
                        points.append([x, y, z])
                        line_count += 1
                    except ValueError:
                        error_count += 1
                        if error_count <= 5:  # 只显示前5个错误
                            print(f"警告：第{line_num}行前三列无法转换为数字: {parts[:3]}")
                else:
                    error_count += 1
                    if error_count <= 5:
                        print(f"警告：第{line_num}行列数不足3列: {len(parts)}列")
        
        if not points:
            print(f"错误：没有读取到任何有效数据！")
            return None
        
        points_array = np.array(points, dtype=np.float64)
        print(f"✓ 成功读取 {len(points_array)} 个点")
        print(f"  跳过空行/注释: {line_num - line_count - error_count} 行")
        print(f"  格式错误行: {error_count} 行")
        
        # 显示前3个点作为示例
        print(f"  前3个点示例:")
        for i in range(min(3, len(points_array))):
            print(f"    点{i+1}: ({points_array[i][0]:.3f}, {points_array[i][1]:.3f}, {points_array[i][2]:.3f})")
        
        return points_array
        
    except Exception as e:
        print(f"读取文件时出错: {e}")
        return None

def find_nearest_neighbors(survey_points, cloud_points):
    """
    为每个全站仪点找到点云中最近的点
    survey_points: (M, 3) 全站仪坐标
    cloud_points: (N, 3) 点云坐标
    返回: (M, 3) 最近点坐标
    """
    print(f"\n{'='*60}")
    print(f"开始查找最近邻点")
    print(f"{'='*60}")
    print(f"全站仪点数量: {len(survey_points)}")
    print(f"点云点数量: {len(cloud_points)}")
    
    # 构建KD树
    print(f"\n正在构建KD树...")
    tree = KDTree(cloud_points)
    
    # 为每个全站仪点查找最近邻
    print(f"正在搜索最近邻点（共{len(survey_points)}个查询）...")
    distances, indices = tree.query(survey_points)
    
    # 统计匹配情况
    unique_matches = len(np.unique(indices))
    print(f"\n匹配统计:")
    print(f"  匹配到的不同点云点数: {unique_matches} / {len(cloud_points)}")
    print(f"  匹配重复率: {(1 - unique_matches/len(cloud_points))*100:.1f}%" if unique_matches < len(cloud_points) else "  无重复匹配")
    
    # 提取最近点（每个全站仪点对应一个点云点）
    nearest_points = cloud_points[indices]
    
    return nearest_points, distances

def save_results(output_file, points):
    """
    保存结果到TXT文件，只保存XYZ三列
    """
    try:
        # 确保输出目录存在
        output_dir = os.path.dirname(output_file)
        if output_dir and not os.path.exists(output_dir):
            os.makedirs(output_dir)
        
        # 保存为三列格式，保留6位小数
        np.savetxt(output_file, points, fmt='%.6f', delimiter=' ', 
                   header=f'X Y Z (Total: {len(points)} points)', 
                   comments='')
        
        print(f"\n✓ 结果已保存到: {output_file}")
        print(f"  文件包含 {len(points)} 个点（每个全站仪点对应一个最近点）")
        return True
        
    except Exception as e:
        print(f"保存文件时出错: {e}")
        return False

def print_detailed_stats(survey_points, nearest_points, distances):
    """
    打印详细统计信息
    """
    print(f"\n{'='*60}")
    print(f"统计信息")
    print(f"{'='*60}")
    
    # 基本统计
    print(f"\n【点数统计】")
    print(f"  全站仪点数: {len(survey_points)}")
    print(f"  输出点数: {len(nearest_points)}")
    print(f"  输出/全站仪比例: {len(nearest_points)/len(survey_points):.0%}")
    
    # 距离统计
    print(f"\n【最近距离统计】")
    print(f"  平均距离: {np.mean(distances):.6f}")
    print(f"  中位数距离: {np.median(distances):.6f}")
    print(f"  最小距离: {np.min(distances):.6f}")
    print(f"  最大距离: {np.max(distances):.6f}")
    print(f"  标准差: {np.std(distances):.6f}")
    
    # 检查输出点是否都相同
    unique_output = np.unique(nearest_points, axis=0)
    print(f"\n【输出点检查】")
    print(f"  输出文件中的唯一点数量: {len(unique_output)}")
    
    if len(unique_output) == 1:
        print(f"  ⚠️  警告：所有输出点都是同一个坐标！")
        print(f"     这个唯一坐标是: ({unique_output[0][0]:.3f}, {unique_output[0][1]:.3f}, {unique_output[0][2]:.3f})")
        print(f"     原因：点云文件中可能只有一个有效点")
    elif len(unique_output) < len(nearest_points):
        print(f"  注意：输出点中有重复（{len(nearest_points)}个输出对应{len(unique_output)}个唯一点）")
    else:
        print(f"  ✓ 所有输出点都是唯一的")
    
    # 显示前10个对应关系
    print(f"\n{'='*60}")
    print(f"前10个点的对应关系")
    print(f"{'='*60}")
    print(f"{'序号':<6} {'全站仪点坐标 (x, y, z)':<35} {'最近点坐标 (x, y, z)':<35} {'距离':<10}")
    print(f"{'-'*90}")
    
    for i in range(min(10, len(survey_points))):
        s = survey_points[i]
        n = nearest_points[i]
        d = distances[i]
        print(f"{i+1:<6} ({s[0]:8.3f}, {s[1]:8.3f}, {s[2]:8.3f})  "
              f"({n[0]:8.3f}, {n[1]:8.3f}, {n[2]:8.3f})  {d:8.4f}")

def main():
    """
    主函数
    """
    print(f"\n{'='*60}")
    print(f"最近邻点查找程序（只处理前三列）")
    print(f"{'='*60}")
    
    # 获取命令行参数或使用默认路径
    if len(sys.argv) == 4:
        survey_file = sys.argv[1]
        cloud_file = sys.argv[2]
        output_file = sys.argv[3]
    else:
        print(f"\n使用方法：")
        print(f"  python {sys.argv[0]} <全站仪文件> <点云文件> <输出文件>")
        print(f"\n示例：")
        print(f"  python {sys.argv[0]} total_station.txt point_cloud.txt result.txt")
        print(f"\n或者直接修改脚本中的默认路径：")
        
        # ========== 请在这里修改为您的实际文件路径 ==========
        survey_file = r"G:\TK-set\桃花\断面\断面\179\全站仪大点坐标.txt"    # 全站仪文件路径
        cloud_file = r"G:\TK-set\桃花\断面\断面\179\点云.txt"# 点云文件路径
        output_file = r"G:\TK-set\桃花\断面\断面\179\最近点坐标.txt"   # 输出文件路径
        # ===================================================
        
        print(f"\n使用默认路径：")
        print(f"  全站仪: {survey_file}")
        print(f"  点云: {cloud_file}")
        print(f"  输出: {output_file}")
        
        response = input(f"\n是否继续？(y/n): ")
        if response.lower() != 'y':
            print("已取消运行。")
            return
    
    # 显示输入文件
    print(f"\n输入文件：")
    print(f"  全站仪文件: {survey_file}")
    print(f"  点云文件: {cloud_file}")
    print(f"  输出文件: {output_file}")
    
    # 步骤1：读取全站仪文件（只取前三列）
    survey_points = read_xyz_only(survey_file, "全站仪文件")
    if survey_points is None:
        return
    
    # 步骤2：读取点云文件（只取前三列）
    cloud_points = read_xyz_only(cloud_file, "点云文件")
    if cloud_points is None:
        return
    
    # 步骤3：查找最近邻
    nearest_points, distances = find_nearest_neighbors(survey_points, cloud_points)
    
    # 步骤4：保存结果
    if save_results(output_file, nearest_points):
        # 步骤5：显示统计信息
        print_detailed_stats(survey_points, nearest_points, distances)
        
        print(f"\n{'='*60}")
        print(f"✓ 程序执行成功！")
        print(f"{'='*60}\n")
    else:
        print(f"\n✗ 程序执行失败！\n")

if __name__ == "__main__":
    main()