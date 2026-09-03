import math


def calculate_fov(focal_length, sensor_size, distance=1.0):
    """
    计算相机视野范围

    参数:
    focal_length: 焦距 (mm)
    sensor_size: 传感器尺寸 (mm) - 可以是单个值(对角线)或元组(宽,高)
    distance: 拍摄距离 (m)，默认为1米

    返回:
    视野范围字典，包含水平和垂直FOV
    """
    # 如果是元组，假设是(宽,高)
    if isinstance(sensor_size, tuple):
        sensor_width, sensor_height = sensor_size
    else:
        # 假设传感器为3:2比例计算宽高
        sensor_width = sensor_size * 3 / math.sqrt(13)  # 3:2对角线
        sensor_height = sensor_size * 2 / math.sqrt(13)

    # 计算视野角度（度）
    h_fov_rad = 2 * math.atan(sensor_width / (2 * focal_length))
    v_fov_rad = 2 * math.atan(sensor_height / (2 * focal_length))

    h_fov_deg = math.degrees(h_fov_rad)
    v_fov_deg = math.degrees(v_fov_rad)

    # 计算在特定距离上的视野范围（米）
    h_fov_m = 2 * distance * math.tan(h_fov_rad / 2)
    v_fov_m = 2 * distance * math.tan(v_fov_rad / 2)

    return {
        '水平视野角度': h_fov_deg,
        '垂直视野角度': v_fov_deg,
        '对角线视野角度': math.degrees(2 * math.atan(
            math.sqrt(sensor_width ** 2 + sensor_height ** 2) / (2 * focal_length)
        )),
        f'在{distance}米处的水平视野宽度': h_fov_m,
        f'在{distance}米处的垂直视野高度': v_fov_m
    }


# 常用传感器尺寸（mm）
SENSOR_SIZES = {
    '1/2.3英寸': (6.17, 4.55),  # 典型手机/小相机
    '1英寸': (13.2, 8.8),  # 高端卡片机
    'Micro Four Thirds': (17.3, 13.0),  # M43
    'APS-C': (23.6, 15.6),  # 多数入门单反
    '全画幅': (36.0, 24.0),  # 全画幅相机
    '中画幅': (43.8, 32.9),  # 中画幅
}