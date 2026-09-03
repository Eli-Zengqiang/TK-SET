from winpty import PtyProcess
from pathlib import Path
import time

def combine_pointcloude_360(exe_args,bat_dir):
    #bat_dir=r"C:\Users\ZHXR\Desktop\com_tool\2.1data\2.1cloud_combine_tool\360度标定合成脚本\360度的部分合成\2.1点云合成.bat"
    parent_batdir=str(Path(bat_dir).parent)
    exit_signal="EXIT_SUCCESS"
    FAILURE_signal="EXIT_FAILURE"
    #exe_name="ScanAndProcess.exe"
    #exe_args0=r"C:\Users\ZHXR\Desktop\发票\2026-06-04_15-07-52/"
    #exe_args1=r"C:\Users\ZHXR\Desktop\发票\2026-06-04_15-07-52\ConfigData-TkSel.cfg"
    exe_args0=exe_args
    exe_args1=exe_args+'\ConfigData-TkSel.cfg'
    exe_path = str(Path(bat_dir).parent)+"\ScanAndProcess.exe"
    #exe_path=r"C:\Users\ZHXR\Desktop\com_tool\2.1data\2.1cloud_combine_tool\360度标定合成脚本\360度的部分合成\ScanAndProcess.exe"
    argv=[exe_path,exe_args0,exe_args1]

    proc = PtyProcess.spawn(argv, cwd=parent_batdir)
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
                if exit_signal in line:
                    print(f"检测到{exit_signal}合成运行结束，准备终止进程")
                    proc.write('\r\n')
                    time.sleep(0.5)
                    # 如果还未退出，强制终止
                    if proc.isalive():
                        proc.terminate()
                    break  # 退出循环
                if FAILURE_signal in line:
                    print(f"检测到{FAILURE_signal}合成运行结束，准备终止进程")
                    proc.write('\r\n')
                    time.sleep(0.5)
                    # 如果还未退出，强制终止
                    if proc.isalive():
                        proc.terminate()
                    break

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
                    if exit_signal in line:
                        print(f"检测到   {line}   合成运行结束，准备终止进程")
                        proc.write('\r\n')
                        time.sleep(0.5)
                        # 如果还未退出，强制终止
                        if proc.isalive():
                            proc.terminate()
                        break  # 退出循环
                    if FAILURE_signal in line:
                        print(f"检测到   {line}   合成运行结束，准备终止进程")
                        proc.write('\r\n')
                        time.sleep(0.5)
                        # 如果还未退出，强制终止
                        if proc.isalive():
                            proc.terminate()
                        break


    except EOFError:
        pass

    proc.close()



if __name__=="__main__":
    exe_args=r"G:\TK-set\2.1data\20260526-4\8CD50\2026-05-20_16-09-15/"#需要合成的文件夹必须为有反斜线'/'  :"C:\Users\ZHXR\Desktop\发票\2026-06-04_15-07-52/"
    bat_dir = r"C:\Users\ZHXR\Desktop\com_tool\2.1data\2.1cloud_combine_tool\360度标定合成脚本\360度的部分合成\2.1点云合成.bat" #.bat文件存放的位置
    combine_pointcloude_360(exe_args,bat_dir)