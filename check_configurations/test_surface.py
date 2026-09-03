import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import subprocess
import threading
import os
import sys


class ScriptLauncher:
    def __init__(self, root):
        self.root = root
        self.root.title("Python 脚本启动器")
        self.root.geometry("500x400")
        self.root.resizable(True, True)

        # 设置样式
        self.style = ttk.Style()
        self.style.configure('TButton', font=('Arial', 10))
        self.style.configure('TLabel', font=('Arial', 10))

        # 创建主框架
        main_frame = ttk.Frame(root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        # 配置网格权重，使界面可调整大小
        root.columnconfigure(0, weight=1)
        root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        main_frame.rowconfigure(5, weight=1)

        # 标题
        title_label = ttk.Label(main_frame, text="Python 脚本启动器",
                                font=('Arial', 16, 'bold'))
        title_label.grid(row=0, column=0, columnspan=3, pady=(0, 20))

        # 脚本选择部分
        script_label = ttk.Label(main_frame, text="选择脚本:")
        script_label.grid(row=1, column=0, sticky=tk.W, pady=5)

        self.script_path = tk.StringVar()
        script_entry = ttk.Entry(main_frame, textvariable=self.script_path, width=40)
        script_entry.grid(row=1, column=1, sticky=(tk.W, tk.E), pady=5, padx=(5, 5))

        browse_button = ttk.Button(main_frame, text="浏览", command=self.browse_script)
        browse_button.grid(row=1, column=2, pady=5)

        # 参数输入部分
        param_label = ttk.Label(main_frame, text="脚本参数:")
        param_label.grid(row=2, column=0, sticky=tk.W, pady=5)

        self.param_entry = ttk.Entry(main_frame, width=40)
        self.param_entry.grid(row=2, column=1, columnspan=2, sticky=(tk.W, tk.E), pady=5)

        # 按钮框架
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=3, column=0, columnspan=3, pady=20)

        self.run_button = ttk.Button(button_frame, text="运行脚本",
                                     command=self.run_script)
        self.run_button.pack(side=tk.LEFT, padx=5)

        self.stop_button = ttk.Button(button_frame, text="停止脚本",
                                      command=self.stop_script, state=tk.DISABLED)
        self.stop_button.pack(side=tk.LEFT, padx=5)

        clear_button = ttk.Button(button_frame, text="清空输出",
                                  command=self.clear_output)
        clear_button.pack(side=tk.LEFT, padx=5)

        # 输出区域
        output_label = ttk.Label(main_frame, text="输出:")
        output_label.grid(row=4, column=0, sticky=tk.W, pady=(10, 5))

        # 创建输出文本框和滚动条
        output_frame = ttk.Frame(main_frame)
        output_frame.grid(row=5, column=0, columnspan=3, sticky=(tk.W, tk.E, tk.N, tk.S), pady=5)

        self.output_text = tk.Text(output_frame, height=15, wrap=tk.WORD)
        output_scrollbar = ttk.Scrollbar(output_frame, orient=tk.VERTICAL,
                                         command=self.output_text.yview)
        self.output_text.configure(yscrollcommand=output_scrollbar.set)

        self.output_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        output_scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))

        output_frame.columnconfigure(0, weight=1)
        output_frame.rowconfigure(0, weight=1)

        # 进程变量
        self.process = None
        self.is_running = False

        # 添加一些示例脚本按钮
        example_frame = ttk.LabelFrame(main_frame, text="示例脚本", padding="5")
        example_frame.grid(row=6, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=10)

        example1_button = ttk.Button(example_frame, text="系统信息",
                                     command=lambda: self.run_example("system_info"))
        example1_button.pack(side=tk.LEFT, padx=5)

        example2_button = ttk.Button(example_frame, text="文件列表",
                                     command=lambda: self.run_example("list_files"))
        example2_button.pack(side=tk.LEFT, padx=5)

        example3_button = ttk.Button(example_frame, text="简单计算",
                                     command=lambda: self.run_example("calculator"))
        example3_button.pack(side=tk.LEFT, padx=5)

        # 初始示例脚本
        self.create_example_scripts()

    def browse_script(self):
        """浏览并选择脚本文件"""
        filename = filedialog.askopenfilename(
            title="选择Python脚本",
            filetypes=[("Python files", "*.py"), ("All files", "*.*")]
        )
        if filename:
            self.script_path.set(filename)

    def run_script(self):
        """运行选定的脚本"""
        script_path = self.script_path.get()

        if not script_path:
            messagebox.showerror("错误", "请先选择一个Python脚本")
            return

        if not os.path.isfile(script_path):
            messagebox.showerror("错误", f"文件不存在: {script_path}")
            return

        # 获取参数
        params = self.param_entry.get().split()

        # 更新按钮状态
        self.run_button.config(state=tk.DISABLED)
        self.stop_button.config(state=tk.NORMAL)
        self.is_running = True

        # 在新线程中运行脚本
        thread = threading.Thread(target=self.execute_script, args=(script_path, params))
        thread.daemon = True
        thread.start()

    def execute_script(self, script_path, params):
        """执行脚本并捕获输出"""
        try:
            # 构建命令
            cmd = [sys.executable, script_path] + params

            # 执行命令
            self.process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                universal_newlines=True,
                bufsize=1
            )

            # 实时读取输出
            for line in iter(self.process.stdout.readline, ''):
                if not self.is_running:
                    break
                self.append_output(line)

            # 等待进程结束
            self.process.wait()

        except Exception as e:
            self.append_output(f"错误: {str(e)}\n")

        # 恢复按钮状态
        self.root.after(0, self.script_finished)

    def stop_script(self):
        """停止正在运行的脚本"""
        if self.process and self.is_running:
            self.is_running = False
            self.process.terminate()
            self.append_output("脚本已停止\n")

    def script_finished(self):
        """脚本执行完成后的回调"""
        self.run_button.config(state=tk.NORMAL)
        self.stop_button.config(state=tk.DISABLED)
        self.append_output("脚本执行完成\n")

    def append_output(self, text):
        """向输出区域添加文本"""
        self.output_text.insert(tk.END, text)
        self.output_text.see(tk.END)
        self.output_text.update_idletasks()

    def clear_output(self):
        """清空输出区域"""
        self.output_text.delete(1.0, tk.END)

    def run_example(self, example_name):
        """运行示例脚本"""
        example_scripts = {
            "system_info": "example_system_info.py",
            "list_files": "example_list_files.py",
            "calculator": "example_calculator.py"
        }

        if example_name in example_scripts:
            script_path = os.path.join(os.path.dirname(__file__), example_scripts[example_name])
            self.script_path.set(script_path)
            self.run_script()

    def create_example_scripts(self):
        """创建示例脚本文件"""
        examples_dir = os.path.dirname(__file__)

        # 系统信息示例脚本
        system_info_script = """#!/usr/bin/env python3
import platform
import os
import datetime

print("=== 系统信息 ===")
print(f"操作系统: {platform.system()} {platform.release()}")
print(f"系统版本: {platform.version()}")
print(f"计算机名: {platform.node()}")
print(f"处理器: {platform.processor()}")
print(f"Python版本: {platform.python_version()}")
print(f"当前用户: {os.getlogin()}")
print(f"当前时间: {datetime.datetime.now()}")
print("=" * 20)
"""

        # 文件列表示例脚本
        list_files_script = """#!/usr/bin/env python3
import os
import sys

path = "." if len(sys.argv) < 2 else sys.argv[1]
print(f"=== 目录内容: {os.path.abspath(path)} ===")

try:
    for item in os.listdir(path):
        item_path = os.path.join(path, item)
        if os.path.isfile(item_path):
            size = os.path.getsize(item_path)
            print(f"文件: {item} ({size} 字节)")
        elif os.path.isdir(item_path):
            print(f"目录: {item}/")
    print("=" * 40)
except Exception as e:
    print(f"错误: {e}")
"""

        # 简单计算示例脚本
        calculator_script = """#!/usr/bin/env python3
import sys

def simple_calculator():
    print("=== 简单计算器 ===")
    print("输入两个数字和操作符 (+, -, *, /)")
    print("例如: 5 3 +")
    print("输入 'quit' 退出")

    while True:
        try:
            user_input = input("计算: ").strip()
            if user_input.lower() == 'quit':
                break

            parts = user_input.split()
            if len(parts) != 3:
                print("格式错误! 请使用: 数字1 数字2 操作符")
                continue

            num1 = float(parts[0])
            num2 = float(parts[1])
            operator = parts[2]

            if operator == '+':
                result = num1 + num2
            elif operator == '-':
                result = num1 - num2
            elif operator == '*':
                result = num1 * num2
            elif operator == '/':
                if num2 == 0:
                    print("错误: 除数不能为零!")
                    continue
                result = num1 / num2
            else:
                print("错误: 不支持的操作符!")
                continue

            print(f"结果: {num1} {operator} {num2} = {result}")

        except ValueError:
            print("错误: 请输入有效的数字!")
        except KeyboardInterrupt:
            print("\\n退出计算器")
            break
        except Exception as e:
            print(f"错误: {e}")

if __name__ == "__main__":
    simple_calculator()
"""

        # 写入示例脚本文件
        scripts = {
            "example_system_info.py": system_info_script,
            "example_list_files.py": list_files_script,
            "example_calculator.py": calculator_script
        }

        for filename, content in scripts.items():
            filepath = os.path.join(examples_dir, filename)
            if not os.path.exists(filepath):
                with open(filepath, 'w') as f:
                    f.write(content)
                # 设置执行权限
                os.chmod(filepath, 0o755)


def main():
    """主函数"""
    root = tk.Tk()
    app = ScriptLauncher(root)
    root.mainloop()


if __name__ == "__main__":
    main()