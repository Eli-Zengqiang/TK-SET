import numpy as np


def calculate_angle_between_components(a, b):
    """
    计算两个三维向量在 x、y、z 方向上的夹角（单位：弧度）

    参数:
        a (np.array): 第一个三维向量，格式 [x, y, z]
        b (np.array): 第二个三维向量，格式 [x, y, z]

    返回:
        dict: 包含 x、y、z 方向夹角的字典（键: 'x', 'y', 'z'）
    """
    angles = {}

    for i, axis in enumerate(['x', 'y', 'z']):
        a_component = a[i]
        b_component = b[i]

        # 如果分量为 0，夹角为 90°（π/2 弧度）
        if a_component == 0 or b_component == 0:
            angle = np.pi / 2
        else:
            # 计算夹角的余弦值
            cos_theta = (a_component * b_component) / (np.abs(a_component) * np.abs(b_component))
            # 处理浮点误差，确保 cos_theta 在 [-1, 1] 范围内
            cos_theta = np.clip(cos_theta, -1.0, 1.0)
            angle = np.arccos(cos_theta)

        angles[axis] = angle

    return angles


# 示例
a = np.array([-0.333853, -0.942316, 0.0241493])  # x 方向向量
b = np.array([0.349954, 0.93629, 0.0299043])  # y 方向向量

angles = calculate_angle_between_components(a, b)
print("各方向夹角（弧度）:", angles)
print("各方向夹角（度）:", {axis: np.degrees(angle) for axis, angle in angles.items()})