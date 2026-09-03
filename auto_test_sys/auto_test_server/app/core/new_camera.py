import argparse
import subprocess
import time
import sys

# 预设分辨率字典
RESOLUTIONS = {
    '12M': (4000, 3000),
    '16M': (5472, 3078),
    '8M': (3264, 2448),
    '4K': (3840, 2160),
    '1080p': (1920, 1080)
}

def set_resolution(device, width, height, pixelformat="MJPG"):
    """设置摄像头分辨率 (Python 3.5兼容)"""
    try:
        subprocess.check_call([
            "v4l2-ctl",
            "-d", device,
            "--set-fmt-video", "width={},height={},pixelformat={}".format(width, height, pixelformat)
        ])
        print("分辨率已设置为: {}x{} ({})".format(width, height, pixelformat))
    except subprocess.CalledProcessError as e:
        raise ValueError("设置分辨率失败: {}".format(e))

def capture_image(device, output):
    """通过v4l2-ctl拍照 (Python 3.5兼容)"""
    try:
        subprocess.check_call([
            "v4l2-ctl",
            "-d", device,
            "--stream-mmap",
            "--stream-count=1",
            "--stream-to", output
        ])
        print("照片已保存为: {}".format(output))
    except subprocess.CalledProcessError as e:
        raise ValueError("拍照失败: {}".format(e))

def list_supported_formats(device):
    """列出支持的分辨率 (Python 3.5兼容)"""
    try:
        output = subprocess.check_output(
            ["v4l2-ctl", "-d", device, "--list-formats-ext"],
            stderr=subprocess.STDOUT
        )
        print("支持的格式与分辨率:\n", output.decode('utf-8'))
    except subprocess.CalledProcessError as e:
        print("获取支持格式失败: {}".format(e.output.decode('utf-8')))


def is_image_valid(file_path):
    try:
        with open(file_path, 'rb') as f:
            header = f.read(32)  # 读取文件头

        # 常见图片格式的文件头
        image_headers = {
            b'\xFF\xD8\xFF': 'jpg',
            b'\x89PNG\r\n\x1a\n': 'png',
            b'GIF87a': 'gif',
            b'GIF89a': 'gif',
            b'BM': 'bmp',
            b'II*\x00': 'tif',
            b'MM\x00*': 'tif'
        }

        for header_bytes, _ in image_headers.items():
            if header.startswith(header_bytes):
                return True
        return False
    except IOError:
        return False

def test_press():
    '''对两个相机进行压力测试'''
    # 4. 设置分辨率并拍照
    set_resolution("/dev/video0", 5472, 3078)
    #set_resolution("/dev/video2", 5472, 3078)
    try:
        for i in range(50):
            capture_image("/dev/video0", "1-{}.jpg".format(i))
            time.sleep(2)  # 等待拍照
            #capture_image("/dev/video2", "2-{}.jpg".format(i))
            #time.sleep(2)  # 等待拍照
            if not is_image_valid("1-{}.jpg".format(i)):
                print("1-{}.jpg 文件有问题".format(i))
            #if not is_image_valid("2-{}.jpg".format(i)):
            #    print("2-{}.jpg 文件有问题".format(i))
    except Exception as e:
        print("错误: {}".format(e))
        sys.exit(1)



def main():
    # 1. 解析命令行参数
    parser = argparse.ArgumentParser(description="通过v4l2-ctl设置分辨率并拍照 (Python 3.5)")
    parser.add_argument("--mode", type=str,
                       choices=RESOLUTIONS.keys(),default="16M",
                       help="分辨率模式（如 '12M', '16M'）")
    parser.add_argument("--output", type=str, required=True,
                       help="输出照片文件名（如 'photo.jpg'）")
    parser.add_argument("--device", type=str, default="/dev/video0",
                       help="摄像头设备路径（默认: /dev/video0）")
    args = parser.parse_args()

    # 2. 检查设备支持的分辨率（可选）
    list_supported_formats(args.device)

    # 3. 获取分辨率
    width, height = RESOLUTIONS[args.mode]

    # 4. 设置分辨率并拍照
    try:
        set_resolution(args.device, width, height)
        time.sleep(2)  # 等待设置生效
        capture_image(args.device, args.output)
    except Exception as e:
        print("错误: {}".format(e))
        sys.exit(1)

if __name__ == "__main__":
    main()
    #test_press()

