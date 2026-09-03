import time
from adafruit_pca9685 import PCA9685
import board

# 初始化PCA9685
i2c = board.I2C()
pca = PCA9685(i2c)
pca.frequency = 50  # 舵机标准频率50Hz [1,3,6](@ref)

# 定义不同舵机的脉冲宽度范围（单位：微秒）
# 180度舵机：0.5ms (0°) 到 2.5ms (180°) [1,6](@ref)
SERVO_180_MIN_PULSE = 500
SERVO_180_MAX_PULSE = 2500
SERVO_180_ANGLE_RANGE = 180

# 270度舵机：通常也是0.5ms (0°) 到 2.5ms (270°)，但请根据您的舵机规格书确认
# 如果您的270度舵机脉冲范围不同（例如0.5ms-2.7ms），请修改下面两行
SERVO_270_MIN_PULSE = 500
SERVO_270_MAX_PULSE = 2500
SERVO_270_ANGLE_RANGE = 270

# 创建一个字典来存储每个通道的舵机类型
# 格式: {通道号: '180'} 或 {通道号: '270'}
# 默认设置：您可以根据实际接线修改默认配置
servo_config = {
    0: '270',   # 通道0接180度舵机
    1: '270',   # 通道1接180度舵机
    2: '270',   # 通道2接270度舵机
    3: '270',   # 通道3接270度舵机
    4: '180',   # 通道3接270度舵机
    5: '180',   # 通道3接270度舵机
    # 4-15通道可以继续配置，不配置则默认为270度
}

# 全局维护每个通道的当前角度（初始为未知）
current_angles = [None] * 16  # 16个通道，初始值为None表示未知

def angle_to_duty_cycle(channel, angle):
    """
    根据通道配置的舵机类型，将角度转换为PCA9685所需的duty_cycle值
    """
    # 获取该通道的舵机类型，如果没有配置则默认为180度
    servo_type = servo_config.get(channel, '270')
    
    if servo_type == '270':
        min_pulse = SERVO_270_MIN_PULSE
        max_pulse = SERVO_270_MAX_PULSE
        max_angle = SERVO_270_ANGLE_RANGE
        servo_name = "270°舵机"
    else:
        min_pulse = SERVO_180_MIN_PULSE
        max_pulse = SERVO_180_MAX_PULSE
        max_angle = SERVO_180_ANGLE_RANGE
        servo_name = "180°舵机"
    
    # 将角度限制在舵机允许范围内
    angle = max(0, min(max_angle, angle))
    
    # 计算脉冲宽度 [3](@ref)
    pulse_width = min_pulse + (angle / max_angle) * (max_pulse - min_pulse)
    
    # 将脉冲宽度转换为duty_cycle（16位精度，0-65535）[3](@ref)
    duty_cycle = int((pulse_width / 20000) * 65535)
    
    print(f"通道 {channel} ({servo_name}): 角度 {angle}° -> 脉冲宽度 {pulse_width:.0f}μs")
    return duty_cycle

def set_servo_angle(channel, angle,need_print=True):
    """设置指定通道的舵机角度"""
    if channel < 0 or channel > 15:
        print("错误：通道号必须在0-15之间")
        return False
    
    # 检查当前角度是否已经等于目标角度
    current_angle = current_angles[channel]
    if current_angle is not None and abs(current_angle - angle) < 0.1:  # 允许0.1度的误差范围
        print(f"→ 通道 {channel} 当前角度 {current_angle:.1f}° 已经接近目标角度 {angle}°，跳过设置")
        return True
    
    try:
        duty_cycle = angle_to_duty_cycle(channel, angle)
        pca.channels[channel].duty_cycle = duty_cycle
        print(f"✓ 已设置通道 {channel} 为 {angle} 度")
        
        # 更新全局角度记录
        current_angles[channel] = angle
        
        # 执行完后打印通道0-5的当前位置
        if need_print:
            print_current_positions()
        
        return True
    except Exception as e:
        print(f"✗ 设置通道 {channel} 时出错: {e}")
        return False

def show_servo_config():
    """显示当前的舵机配置"""
    print("\n当前舵机配置:")
    for channel in range(16):
        servo_type = servo_config.get(channel, '270')
        print(f"  通道 {channel}: {servo_type}度舵机")

def print_current_positions():
    """打印通道0-5的当前位置"""
    print("\n通道0-5当前角度状态:")
    for channel in range(6):  # 只打印通道0-5
        servo_type = servo_config.get(channel, '270')
        current_angle = current_angles[channel]
        if current_angle is None:
            angle_display = "未知"
        else:
            angle_display = f"{current_angle}°"
        print(f"  通道 {channel} ({servo_type}°舵机): {angle_display}")

def main():
    print("=" * 60)
    print("PCA9685 多类型舵机调试工具 (支持180°/270°舵机)")
    print("=" * 60)
    show_servo_config()
    print("\n指令说明:")
    print("  [通道] [角度]    - 设置指定通道的角度 (例如: 0 90)")
    print("  config [通道] [类型] - 更改通道配置 (例如: config 5 270)")
    print("  sweep [通道]     - 让指定通道的舵机在其角度范围内扫掠")
    print("  center          - 将所有通道设置到中间角度")
    print("  stop            - 停止所有通道的PWM信号")
    print("  config          - 显示当前舵机配置")
    print("  quit            - 退出程序")
    print("-" * 60)
    
    try:
        while True:
            user_input = input("\n输入指令: ").strip()
            
            if user_input.lower() == 'quit':
                print("退出调试工具。")
                break
            elif user_input.lower() == 'center':
                print("正在将所有通道设置到中间角度...")
                for channel in range(16):
                    servo_type = servo_config.get(channel, '180')
                    middle_angle = 90 if servo_type == '180' else 135
                    set_servo_angle(channel, middle_angle)
                    time.sleep(0.1)
            elif user_input.lower() == 'stop':
                print("正在停止所有通道...")
                for channel in range(16):
                    pca.channels[channel].duty_cycle = 0
                print("✓ 所有通道已停止")
            elif user_input.lower() == 'config':
                show_servo_config()
            elif user_input.lower().startswith('config '):
                try:
                    parts = user_input.split()
                    channel = int(parts[1])
                    new_type = parts[2]
                    
                    if channel < 0 or channel > 15:
                        print("错误：通道号必须在0-15之间")
                    elif new_type not in ['180', '270']:
                        print("错误：舵机类型必须是'180'或'270'")
                    else:
                        servo_config[channel] = new_type
                        print(f"✓ 通道 {channel} 已配置为 {new_type}度舵机")
                        show_servo_config()
                except (ValueError, IndexError):
                    print("错误：配置指令格式不正确。使用 'config [通道] [类型]'")
            elif user_input.lower().startswith('sweep'):
                try:
                    parts = user_input.split()
                    sweep_channel = int(parts[1]) if len(parts) > 1 else 0
                    
                    if 0 <= sweep_channel <= 15:
                        servo_type = servo_config.get(sweep_channel, '180')
                        if servo_type == '180':
                            angles = [0, 45, 90, 135, 180, 135, 90, 45, 0]
                        else:
                            angles = [0, 67, 135, 202, 270, 202, 135, 67, 0]
                        
                        print(f"正在让通道 {sweep_channel} 的{servo_type}度舵机进行扫掠运动...")
                        for angle in angles:
                            set_servo_angle(sweep_channel, angle)
                            time.sleep(0.5)
                    else:
                        print("错误：通道号必须在0-15之间")
                except (ValueError, IndexError):
                    print("错误：扫掠指令格式不正确。使用 'sweep' 或 'sweep [通道]'")
            else:
                # 尝试解析为 [通道] [角度] 格式
                try:
                    parts = user_input.split()
                    if len(parts) == 2:
                        channel = int(parts[0])
                        angle = float(parts[1])
                        set_servo_angle(channel, angle)
                    else:
                        print("错误：指令格式不正确。使用 '[通道] [角度]'")
                except ValueError:
                    print("错误：请输入有效的数字")
                    
    except KeyboardInterrupt:
        print("\n\n程序被用户中断")
    finally:
        # 程序退出前清理资源
        print("正在清理资源...")
        for channel in range(16):
            pca.channels[channel].duty_cycle = 0
        print("调试工具已安全关闭")

if __name__ == "__main__":
    main()