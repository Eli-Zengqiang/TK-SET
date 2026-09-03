import subprocess

import subprocess
import time
import os
import signal


def start_app():
        """启动应用，返回进程对象"""
        proc = subprocess.Popen(
                "./zshy2_app",
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                shell=True
        )

        print(f"应用已启动，PID: {proc.pid}")
        #proc.communicate(timeout=50)

        return proc


def stop_app(proc=None):
        """停止应用"""
        if proc:
                # 方法1: 使用进程对象
                proc.terminate()
                print("终止进程")
                try:
                        std_out, std_err = proc.communicate()
                        print("proc.terminate生效")
                        print(std_out)


                        proc.wait(timeout=10)
                        return True
                except:
                        proc.kill()
                        #proc.wait()
                        print("proc.kill生效")
                        std_out, std_err = proc.communicate()
                        print(std_out)
                        return True


        # # 方法2: 通过名称查找
        # try:
        #         # 使用pkill直接杀死
        #         subprocess.run(["pkill", "-f", "zshy2_app"], timeout=30)
        #         # 确保杀死
        #         subprocess.run(["pkill", "-9", "-f", "zshy2_app"], timeout=30)
        #         return True
        # except:
        #         return False


# 主要逻辑
if __name__ == '__main__':

        for i in range(3):
                print(f"第{i+1}次循环")
                # 启动并运行10秒
                process = start_app()
                try:
                        # 运行10秒
                        time.sleep(70)
                finally:
                        # 无论如何都尝试关闭
                        stop_app(process)
                        print("应用已关闭")



