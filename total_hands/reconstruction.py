from PyQt5.QtCore import Qt, QThread, pyqtSignal
import subprocess
from paths import *


class ReconstructionThread(QThread):
    my_signal = pyqtSignal(str)
    my_signal_1 = pyqtSignal(str)

    def __init__(self,path0,path1):
        super(ReconstructionThread, self).__init__()
        self.path0=path0
        self.path1 = path1


    def run(self):
        self.run_exe(self.path0,self.path1)

    def run_exe(self,path0,path1):
        cmd = ReconstructionExe_path+" "+path0+"\\ "+path1
        cmd = cmd.replace("/", "\\")
        p = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        out_str=''
        for i in iter(p.stdout.readline, ''):
            if i == b'':
                break
            temp_str = i.strip().decode(encoding="gbk")
            print(temp_str)
            find_index = temp_str.find("EXIT_SUCCESS")
            if find_index != -1:
                out_str = temp_str[find_index:]
            self.my_signal.emit(temp_str)
        self.my_signal_1.emit(out_str)#返回结果
