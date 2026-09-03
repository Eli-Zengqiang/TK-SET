#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sys, io, os, numpy as np
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', write_through=True)
total_station=[-1.1139318943,8.10792255402,4.10205602646]  #全站仪设站坐标

#DIR = os.path.dirname(os.path.abspath(sys.argv[0]))
DIR = os.path.dirname(r"G:\TK-set\实验\象印科技\象印攀枝花测试\Export\象印\1.txt")
a1 = os.path.join(DIR, "1.txt")   #全站仪打点
a2 = os.path.join(DIR, "2.txt")     #扫描仪点云
a3 = os.path.join(DIR, "3.txt")   #测试误差
# 读取文件（前三列为xyz）
pts1 = np.loadtxt(a1, usecols=(0, 1, 2))
pts2 = np.loadtxt(a2, usecols=(0, 1, 2))

print(f"1.txt: {len(pts1)} 个点")
print(f"2.TXT: {len(pts2)} 个点")

# 读取2.TXT完整内容（保留所有列）
pts2_full = np.loadtxt(a2)

K = 6  # 最近邻数量

with open(a3, "w", encoding="utf-8") as f:
    for i, p1 in enumerate(pts1):
        # 计算p1到pts2所有点的距离
        diffs = pts2[:, :3] - p1[:3]
        dists = np.sqrt(np.sum(diffs ** 2, axis=1))
        # 取最近的6个点的索引
        idx = np.argsort(dists)[:K]
        # 写入：查询点xyz + 每个最近点的所有列数据
        f.write(f"查询点 {i}: {p1[0]:.4f} {p1[1]:.4f} {p1[2]:.4f}\n")
        for j in idx:
            vals = " ".join(f"{v:.4f}" for v in pts2_full[j])
            f.write(f"  {vals}  距离={dists[j]:.4f}\n")
        f.write("\n")

print("完成，结果已写入 a3.txt")

