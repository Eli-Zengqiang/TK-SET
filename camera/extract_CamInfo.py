import re
import sys
import os


def extract_and_save(input_file, output_file):
    with open(input_file, 'r', encoding='utf-8') as f:
        content = f.read()

    # 提取内参矩阵 (3x3)
    # 匹配 "内参矩阵" 后紧跟的三行数字
    intrinsic_pattern = r'内参矩阵.*?\n\s*([-\d.]+\s+[-\d.]+\s+[-\d.]+)\s*\n\s*([-\d.]+\s+[-\d.]+\s+[-\d.]+)\s*\n\s*([-\d.]+\s+[-\d.]+\s+[-\d.]+)'
    intrinsic_match = re.search(intrinsic_pattern, content, re.DOTALL)
    if not intrinsic_match:
        raise ValueError("未找到内参矩阵")

    # 提取畸变系数 (k1 k2 p1 p2)
    distortion_pattern = r'畸变系数.*?\n\s*([-\d.]+\s+[-\d.]+\s+[-\d.]+\s+[-\d.]+)'
    distortion_match = re.search(distortion_pattern, content)
    if not distortion_match:
        raise ValueError("未找到畸变系数")

    # 拼接输出内容：3行矩阵 + 1行畸变系数
    output_lines = [
        intrinsic_match.group(1),
        intrinsic_match.group(2),
        intrinsic_match.group(3),
        distortion_match.group(1)
    ]

    with open(output_file, 'w', encoding='utf-8') as f:
        f.write('\n'.join(output_lines))

    print(f"成功提取并保存到: {output_file}")


if __name__ == "__main__":
    # if len(sys.argv) != 3:
    #     print("用法: python extract.py <输入文件> <输出文件>")
    #     sys.exit(1)
    # extract_and_save(sys.argv[1], sys.argv[2])
    # output_file=r"G:\TK-set\2.1data\20260408-2\34C051\0\camerainfo.txt"
    # input_file=r"G:\TK-set\2.1data\20260408-2\34C051\0\24.txt"
    # extract_and_save(input_file, output_file)

    path=r"G:\TK-set\实验\自动化相机标定_40镜头相机内参"
    out_path=r"G:\TK-set\实验\自动化相机标定_40镜头相机内参\提取参数"
    camera_list=os.listdir(path)
    camera_list=sorted(camera_list)
    for camera in camera_list:
        if ".txt" not in camera:
            continue
        else:
            input_file=os.path.join(path,camera)
            print(input_file)
            output_file=os.path.join(out_path,camera.split(".")[0]+".txt")
            extract_and_save(input_file, output_file)