#!/usr/bin/env python3
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
            print("\n退出计算器")
            break
        except Exception as e:
            print(f"错误: {e}")

if __name__ == "__main__":
    simple_calculator()
