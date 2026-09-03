import subprocess
import sys
import os
import time
import shutil

###修改.bat文件中的路径
real_path=r"G:\TK-set\2.1data\20260421\9BA26无点云重新采集\2026-04-21_11-15-32/"
real_content=r"ScanAndProcess.exe "+real_path
shutil.copy(r"C:\Users\ZHXR\Desktop\com_tool\2.1data\2.1cloud_combine_tool\标定-0516\TestBox.txt", real_path)
shutil.copy(r"C:\Users\ZHXR\Desktop\com_tool\2.1data\2.1cloud_combine_tool\标定-0516\GeoBox.txt", real_path)

bat_path = sys.argv[1] if len(sys.argv) > 1 else r"C:\Users\ZHXR\Desktop\com_tool\2.1data\2.1cloud_combine_tool\标定-0516\180标定-0.5\智隧慧眼2.1标定.bat"
bat_dir = os.path.dirname(bat_path)

# 读取原 .bat，去掉 pause
# with open(bat_path, 'r', encoding='gbk') as f:
#     content = f.read()
#
# # 去掉各种 pause 写法
# content = re.sub(r'&?\s*pause\s*', '', content, flags=re.IGNORECASE)
with open(bat_path, 'r', encoding='gbk') as f:
    content = f.readlines()
    content[0]=real_content
    content[1] = ''
    content[2] = ''


# 写到同目录下的临时文件
temp_bat = os.path.join(bat_dir, '_run_temp.bat')
with open(temp_bat, 'w', encoding='gbk') as f:
    f.writelines(content)

# 在新窗口中运行（不设 stdin pipe，窗口正常显示）
subprocess.Popen(
    ['cmd', '/c', temp_bat],
    cwd=bat_dir,
    creationflags=subprocess.CREATE_NEW_CONSOLE
)

# 等一会儿后清理临时文件
time.sleep(30)
try:
    if os.path.exists(temp_bat):
        os.unlink(temp_bat)
except:
    pass
