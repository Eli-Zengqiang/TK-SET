import sys
import os
import re
from winpty import PtyProcess
import time
import shutil
from  prism_ball.CfgClass import CfgClass
from pathlib import Path

def parse_angles(line, angles):
    for m in re.finditer(r'安装([XYZ])角度[为=]([-\d.]+)', line):
        name = f'雷达安装{m.group(1)}角度'
        val = float(m.group(2))
        for i, (n, _) in enumerate(angles):
            if n == name:
                angles[i] = (name, val)
                break
        else:
            angles.append((name, val))
    for m in re.finditer(r'全站仪安装把手角度[为=]([-\d.]+)', line):
        name = '全站仪安装把手角度'
        val = float(m.group(1))
        for i, (n, _) in enumerate(angles):
            if n == name:
                angles[i] = (name, val)
                break
        else:
            angles.append((name, val))


def run_bat_to_calibrate(bat_path,data_path):    #bat_path:标定文件.bat的位置；data_path：需要标定的数据位置
    #data_path = r"G:\TK-set\2.1data\20260421\9BA26无点云重新采集\2026-04-21_11-15-32/"
    parent_path=str(Path(data_path).parent) + '/'
    real_path = data_path
    print(f"复制包围盒到该路径下：{real_path}")
    bat_dir = os.path.dirname(bat_path)
    ####拷贝TestBox.txt、GeoBox.txt到目标文件（从标定脚本.bat所在目录读取）
    shutil.copy(os.path.join(bat_dir, "TestBox.txt"), real_path)
    shutil.copy(os.path.join(bat_dir, "GeoBox.txt"), real_path)
    real_content = r"ScanAndProcess.exe " + real_path
    #bat_path = sys.argv[1] if len(sys.argv) > 1 else r"C:\Users\ZHXR\Desktop\com_tool\2.1data\2.1cloud_combine_tool\标定-0516\180标定-0.5\智隧慧眼2.1标定.bat"
    bat_dir = os.path.dirname(bat_path)

    with open(bat_path, 'r', encoding='gbk') as f:
        content = f.readlines()
        content[0] = real_content+'\n'
        # content[1] = ''
        # content[2] = ''

    # 写到同目录下的临时文件
    temp_bat = os.path.join(bat_dir, '_run_temp.bat')
    with open(temp_bat, 'w', encoding='gbk') as a:
        a.writelines(content)


    with open(temp_bat, 'r', encoding='gbk') as b:
        bat_content = b.read()
        # print(bat_content)

    #######去除.bat文件中的带有：echoxxxxx，remark，pause的行
    for bline in bat_content.splitlines():
        bline = bline.strip()
        if bline and not any(bline.startswith(x) for x in ('@', 'echo', 'cd', 'rem', 'pause')):
            parts = bline.split(None, 1)
            exe_name, exe_args = parts[0], parts[1] if len(parts) > 1 else ''
            break

    exe_path = os.path.join(bat_dir, exe_name)

    argv = [exe_path] + (exe_args.split() if exe_args else [])
    print(argv)
    print(f"运行: {exe_path} {' '.join(argv[1:])}")

    proc = PtyProcess.spawn(argv, cwd=bat_dir)
    angles = []
    handle_angles=[]

    try:
        while proc.isalive():
            try:
                line = proc.readline()
            except EOFError:
                break
            if not line:
                continue
            line = line.rstrip('\n\r')
            if line:
                print(line, flush=True)
                parse_angles(line, angles)
    except EOFError:
        pass

    # 读取剩余输出
    try:
        remaining = proc.read()
        if remaining:
            for line in remaining.split('\n'):
                line = line.rstrip('\r')
                if line:
                    print(line, flush=True)
                    parse_angles(line, angles)
    except EOFError:
        pass

    proc.close()

    if angles:
        print(f"\n提取的角度列表:")
        print(angles)
        for name, val in angles:
            print(f"  {name}: {val}")
    else:
        print("\n未提取到任何角度")

    with open(os.path.join(parent_path, '标定angles.txt'), 'w', encoding='gbk') as f:  #os.path.join(bat_dir, 'angles.txt')
        for name, val in angles:
            f.write(f"{name}: {val}\n")
            handle_angles.append(val)
    #print(f"角度已保存到: {os.path.join(bat_dir, 'angles.txt')}")
    print(f"角度已保存到: {os.path.join(parent_path, '标定angles.txt')}")

    time.sleep(30)
    try:
        if os.path.exists(temp_bat):
            os.unlink(temp_bat)
    except:
        pass
    print(handle_angles)
    return  handle_angles



if __name__=="__main__":
    #需要标定的数据文件路径
    data_path=r"G:\TK-set\2.1data\20260708-EC857\EC857\2025-12-17_16-58-10/"
    #斌哥标定脚本的路径
    bat_path =  r"C:\Users\ZHXR\Desktop\com_tool\2.1data\2.1cloud_combine_tool\标定-0516\180标定-0.5\智隧慧眼2.1标定.bat"
    #标定雷达角度、把手角度
    hand_angles=run_bat_to_calibrate(bat_path,data_path)
    #cfg路径
    cfg_path=data_path+"ConfigData-TkSel.cfg"
    sa=CfgClass()
    #打开cfg
    sa.readFromCFG(cfg_path)
    #写入雷达安装角度
    sa.corret_file_cfg(hand_angles[0],hand_angles[2])
    #写入站仪把手角度
    sa.TotalStationOffsetAngle_cfg(hand_angles[3])
    #保存cfg
    sa.saveFile(cfg_path)
