from datetime import datetime

timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')  # 获取当前时间并格式化为字符串,strftime只能格式化到s。
milliseconds = datetime.now().microsecond  # 获取us时间
timestamps = f"{timestamp}.{milliseconds}"

timestamp1 = 1745936628.6999094

# 提取整数秒和小数部分（毫秒）
total_seconds = int(timestamp1)
milliseconds = int((timestamp1 - total_seconds) * 1000)

# 计算时分秒
seconds_in_day = total_seconds % (24 * 3600)
hours = seconds_in_day // 3600
minutes = (seconds_in_day % 3600) // 60
seconds = seconds_in_day % 60

# 格式化输出（HH:MM:SS）
time_str = f"{hours:02d}:{minutes:02d}:{seconds:02d}"
print(time_str)  # 输出：13:23:48

# 如果需要毫秒
time_with_ms = f"{hours:02d}:{minutes:02d}:{seconds:02d}.{milliseconds:03d}"
print(time_with_ms)  # 输出：13:23:48.699