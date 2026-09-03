import pyaudio
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
import threading
import time
from collections import deque
import wave
import struct
import os
from datetime import datetime
import warnings

warnings.filterwarnings('ignore')


class AudioMutantDetector:
    def __init__(self,
                 rate=44100,
                 chunk_size=1024,
                 history_seconds=5,
                 threshold_multiplier=2.0,
                 min_threshold=0.01,
                 save_duration=4,  # 保存前后总共4秒
                 save_directory="recordings"):
        """
        初始化音频突变检测器

        Args:
            rate: 采样率
            chunk_size: 每次读取的音频块大小
            history_seconds: 历史数据窗口时间（秒）
            threshold_multiplier: 阈值倍数（相对历史均值的倍数）
            min_threshold: 最小阈值，避免静音时误报
            save_duration: 保存的音频总时长（秒），前后各一半
            save_directory: 保存录音的目录
        """
        self.rate = rate
        self.chunk_size = chunk_size
        self.history_seconds = history_seconds
        self.threshold_multiplier = threshold_multiplier
        self.min_threshold = min_threshold
        self.save_duration = save_duration
        self.pre_duration = save_duration // 2  # 突变前保存的秒数
        self.post_duration = save_duration - self.pre_duration  # 突变后保存的秒数
        self.save_directory = save_directory

        # 创建保存目录
        if not os.path.exists(save_directory):
            os.makedirs(save_directory)
            print(f"创建录音保存目录: {save_directory}")

        # 初始化PyAudio
        self.p = pyaudio.PyAudio()
        self.stream = None

        # 数据缓冲区
        self.history_buffer = deque(maxlen=int(rate * history_seconds / chunk_size))
        self.audio_buffer = deque(maxlen=100)  # 用于显示

        # 循环缓冲区用于保存音频（保存最近N秒的音频数据）
        self.circular_buffer_size = int(rate * save_duration / chunk_size) + 10
        self.circular_buffer = deque(maxlen=self.circular_buffer_size)
        self.raw_audio_buffer = deque(maxlen=self.circular_buffer_size)  # 保存原始音频数据

        # 状态变量
        self.is_recording = False
        self.mutant_detected = False
        self.last_mutant_time = 0
        self.mutant_cooldown = 2.0  # 突变检测冷却时间（秒）
        self.saving_in_progress = False

        # 统计信息
        self.rms_values = []
        self.threshold_values = []
        self.mutant_times = []
        self.saved_files = []  # 记录保存的文件名

        # 可视化相关
        self.fig, (self.ax1, self.ax2) = plt.subplots(2, 1, figsize=(12, 8))

    def calculate_rms(self, data):
        """计算音频块的RMS值"""
        try:
            # 将字节数据转换为整数数组
            fmt = f"{len(data) // 2}h"
            int_data = struct.unpack(fmt, data)
            # 转换为numpy数组并归一化
            audio_array = np.array(int_data, dtype=np.float32) / 32768.0
            # 计算RMS
            rms = np.sqrt(np.mean(audio_array ** 2))
            return rms, audio_array, int_data
        except:
            return 0.0, np.zeros(self.chunk_size), []

    def calculate_threshold(self):
        """计算动态阈值"""
        if len(self.history_buffer) < 10:
            return self.min_threshold

        # 计算历史RMS的均值和标准差
        history_array = np.array(list(self.history_buffer)[-50:])  # 使用最近50个值
        mean_rms = np.mean(history_array)
        std_rms = np.std(history_array)

        # 阈值 = 均值 + 倍数 * 标准差
        threshold = mean_rms + self.threshold_multiplier * std_rms
        return max(threshold, self.min_threshold)

    def detect_mutant(self, current_rms):
        """检测是否发生突变"""
        if len(self.history_buffer) < 5:
            return False

        threshold = self.calculate_threshold()

        # 检查是否超过阈值
        if current_rms > threshold:
            # 冷却时间检查
            current_time = time.time()
            if current_time - self.last_mutant_time > self.mutant_cooldown:
                return True

        return False

    def save_audio_segment(self, mutant_time):
        """保存突变前后的音频段"""
        if self.saving_in_progress:
            return

        self.saving_in_progress = True

        try:
            # 生成文件名（使用时间戳）
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"mutant_{timestamp}_rms{self.rms_values[-1]:.3f}.wav"
            filepath = os.path.join(self.save_directory, filename)

            # 从循环缓冲区获取要保存的数据
            buffer_list = list(self.raw_audio_buffer)

            if len(buffer_list) < 10:
                print("  缓冲区数据不足，无法保存")
                self.saving_in_progress = False
                return

            # 计算要保存的数据范围
            total_chunks_needed = int(self.save_duration * self.rate / self.chunk_size)

            # 如果缓冲区数据不够，保存所有数据
            if len(buffer_list) < total_chunks_needed:
                chunks_to_save = buffer_list
                print(f"  警告: 缓冲区数据不足，仅保存 {len(chunks_to_save)} 个块")
            else:
                # 取最后total_chunks_needed个块
                chunks_to_save = buffer_list[-total_chunks_needed:]

            # 合并所有音频数据
            audio_data = b''.join(chunks_to_save)

            # 保存为WAV文件
            with wave.open(filepath, 'wb') as wf:
                wf.setnchannels(1)  # 单声道
                wf.setsampwidth(2)  # 16-bit = 2 bytes
                wf.setframerate(self.rate)
                wf.writeframes(audio_data)

            # 计算实际时长
            actual_duration = len(chunks_to_save) * self.chunk_size / self.rate

            # 记录保存的文件
            self.saved_files.append(filepath)
            print(f"\n  💾 音频已保存: {filename}")
            print(f"     时长: {actual_duration:.2f}秒, 大小: {len(audio_data) / 1024:.1f}KB")

            # 可选：打印更多信息
            print(f"     触发RMS: {self.rms_values[-1]:.4f}, 阈值: {self.threshold_values[-1]:.4f}")

        except Exception as e:
            print(f"  保存音频时出错: {e}")

        self.saving_in_progress = False

    def audio_callback(self, in_data, frame_count, time_info, status):
        """音频数据回调函数"""
        if not self.is_recording:
            return (in_data, pyaudio.paContinue)

        # 计算RMS
        rms, audio_array, int_data = self.calculate_rms(in_data)

        # 保存原始音频数据到循环缓冲区
        self.raw_audio_buffer.append(in_data)

        # 更新历史缓冲区（用于计算阈值）
        self.history_buffer.append(rms)

        # 更新循环缓冲区（用于可视化）
        self.audio_buffer.append(audio_array)

        # 检测突变
        if self.detect_mutant(rms):
            current_time = time.time()
            self.mutant_detected = True
            self.last_mutant_time = current_time
            self.mutant_times.append(current_time)

            # 打印检测信息
            threshold = self.calculate_threshold()
            print(f"\n⚠️ 检测到音频突变!")
            print(f"   RMS: {rms:.4f}, 阈值: {threshold:.4f}")

            # 在新线程中保存音频，避免阻塞音频流
            save_thread = threading.Thread(target=self.save_audio_segment, args=(current_time,))
            save_thread.daemon = True
            save_thread.start()
        else:
            self.mutant_detected = False

        # 保存RMS值用于可视化
        self.rms_values.append(rms)
        self.threshold_values.append(self.calculate_threshold())

        return (in_data, pyaudio.paContinue)

    def start_recording(self):
        """开始录音"""
        try:
            self.stream = self.p.open(
                format=pyaudio.paInt16,
                channels=1,
                rate=self.rate,
                input=True,
                frames_per_buffer=self.chunk_size,
                stream_callback=self.audio_callback
            )
            self.is_recording = True
            print("\n" + "=" * 60)
            print("音频突变检测系统已启动")
            print("=" * 60)
            print(f"采样率: {self.rate}Hz")
            print(f"块大小: {self.chunk_size}")
            print(f"阈值倍数: {self.threshold_multiplier}")
            print(f"最小阈值: {self.min_threshold}")
            print(f"录音保存时长: {self.save_duration}秒 (前后各{self.pre_duration}秒)")
            print(f"保存目录: {self.save_directory}")
            print("\n操作指南:")
            print("- 正常说话: 产生连续音频")
            print("- 拍手/敲击: 触发突变检测并自动保存")
            print("- 突变冷却时间: 2秒 (避免重复保存)")
            print("- 关闭窗口或按Ctrl+C退出")
            print("=" * 60 + "\n")
        except Exception as e:
            print(f"无法打开麦克风: {e}")
            return False
        return True

    def stop_recording(self):
        """停止录音"""
        self.is_recording = False
        if self.stream:
            self.stream.stop_stream()
            self.stream.close()
        self.p.terminate()

        # 显示统计信息
        print("\n" + "=" * 60)
        print("录音已停止 - 统计信息")
        print("=" * 60)
        print(f"检测到突变次数: {len(self.mutant_times)}")
        print(f"保存的文件数量: {len(self.saved_files)}")
        if self.saved_files:
            print("\n保存的文件列表:")
            for i, file in enumerate(self.saved_files[-5:], 1):
                print(f"  {i}. {os.path.basename(file)}")
            if len(self.saved_files) > 5:
                print(f"  ... 还有 {len(self.saved_files) - 5} 个文件")
        print("=" * 60)

    def update_plot(self, frame):
        """更新可视化图表"""
        if len(self.rms_values) == 0:
            return

        # 清除并重绘
        self.ax1.clear()
        self.ax2.clear()
        plt.rcParams['font.sans-serif'] = ['SimHei']  # 指定默认字体
        plt.rcParams['axes.unicode_minus'] = False

        # 绘制波形图（最近的数据）
        if len(self.audio_buffer) > 0:
            recent_audio = self.audio_buffer[-1][:500]  # 显示前500个点
            self.ax1.plot(recent_audio, color='blue', alpha=0.7)
            self.ax1.set_title('实时音频波形')
            self.ax1.set_ylabel('振幅')
            self.ax1.set_ylim(-1, 1)
            self.ax1.grid(True, alpha=0.3)

            # 如果检测到突变，标记
            if self.mutant_detected:
                self.ax1.axvspan(0, 500, alpha=0.3, color='red')
                self.ax1.text(10, 0.8, '突变检测!', color='red', fontsize=12, weight='bold')
                self.ax1.text(10, 0.6, '正在保存...', color='orange', fontsize=10)

        # 绘制RMS和阈值曲线
        recent_rms = self.rms_values[-200:]  # 显示最近200个点
        recent_threshold = self.threshold_values[-200:]
        x = range(len(recent_rms))

        self.ax2.plot(x, recent_rms, color='blue', label='RMS值', linewidth=1)
        self.ax2.plot(x, recent_threshold, color='red', label='动态阈值', linewidth=2, linestyle='--')
        self.ax2.set_title('音频RMS与突变检测阈值')
        self.ax2.set_xlabel('时间 (块)')
        self.ax2.set_ylabel('RMS')
        self.ax2.legend(loc='upper right')
        self.ax2.grid(True, alpha=0.3)

        # 标记突变点
        if len(self.mutant_times) > 0:
            # 在图上标记最近几个突变点
            for i, t in enumerate(self.mutant_times[-3:]):
                self.ax2.axvline(x=len(recent_rms) - 1 - i * 20, color='red', alpha=0.5, linestyle=':', linewidth=2)

        # 显示统计信息
        info_text = f"突变次数: {len(self.mutant_times)} | 保存文件: {len(self.saved_files)}"
        self.ax2.text(0.02, 0.95, info_text, transform=self.ax2.transAxes,
                      bbox=dict(boxstyle="round,pad=0.3", facecolor="yellow", alpha=0.7))

        plt.tight_layout()


    def run(self):
        """运行主程序"""
        if not self.start_recording():
            return

        # 设置动画
        ani = FuncAnimation(self.fig, self.update_plot, interval=50, cache_frame_data=False)

        try:
            plt.show()
        except KeyboardInterrupt:
            print("\n用户中断")
        finally:
            self.stop_recording()


class AdvancedAudioDetector(AudioMutantDetector):
    """高级音频检测器，增加更多特征"""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # 增加频谱历史
        self.spectrum_history = deque(maxlen=50)

    def calculate_spectrum_rms(self, audio_array):
        """计算频谱RMS"""
        try:
            # 计算FFT
            fft_data = np.fft.fft(audio_array)
            magnitude = np.abs(fft_data[:len(fft_data) // 2])
            # 计算频谱能量
            spectrum_rms = np.sqrt(np.mean(magnitude ** 2))
            return spectrum_rms
        except:
            return 0.0

    def audio_callback(self, in_data, frame_count, time_info, status):
        """增强的回调函数"""
        if not self.is_recording:
            return (in_data, pyaudio.paContinue)

        # 计算RMS
        rms, audio_array, int_data = self.calculate_rms(in_data)

        # 计算频谱特征
        spectrum_rms = self.calculate_spectrum_rms(audio_array)

        # 综合特征（可以加权组合）
        # 需要适当缩放频谱RMS
        scaled_spectrum = spectrum_rms / 1000  # 粗略缩放
        combined_feature = 0.6 * rms + 0.4 * scaled_spectrum

        # 保存原始音频数据
        self.raw_audio_buffer.append(in_data)

        # 更新历史缓冲区（使用综合特征）
        self.history_buffer.append(combined_feature)

        # 更新可视化缓冲区
        self.audio_buffer.append(audio_array)

        # 检测突变
        if self.detect_mutant(combined_feature):
            current_time = time.time()
            self.mutant_detected = True
            self.last_mutant_time = current_time
            self.mutant_times.append(current_time)

            threshold = self.calculate_threshold()
            print(f"\n⚠️ 检测到音频突变!")
            print(f"   RMS: {rms:.4f}, 频谱能量: {spectrum_rms:.1f}")
            print(f"   综合特征: {combined_feature:.4f}, 阈值: {threshold:.4f}")

            # 在新线程中保存音频
            save_thread = threading.Thread(target=self.save_audio_segment, args=(current_time,))
            save_thread.daemon = True
            save_thread.start()
        else:
            self.mutant_detected = False

        # 保存数据用于可视化
        self.rms_values.append(rms)
        self.threshold_values.append(self.calculate_threshold())

        return (in_data, pyaudio.paContinue)


def main():
    """主函数"""
    print("=" * 60)
    print("音频突变检测系统 - 带录音保存功能")
    print("=" * 60)

    # 选择检测模式
    print("\n请选择检测模式:")
    print("1. 基础模式 (音量突变检测)")
    print("2. 高级模式 (音量+频谱分析)")

    choice = input("请输入选择 (1/2) [默认:1]: ").strip() or "1"

    # 配置参数
    config = {
        'rate': 44100,
        'chunk_size': 1024,
        'history_seconds': 3,
        'threshold_multiplier': 3.0,
        'min_threshold': 0.01,
        'save_duration': 4,  # 保存前后共4秒
        'save_directory': "mutant_recordings"
    }

    # 允许自定义参数
    custom = input("\n是否自定义参数? (y/n) [默认:n]: ").strip().lower()
    if custom == 'y':
        try:
            config['threshold_multiplier'] = float(input("阈值倍数 (建议2.0-5.0) [默认:3.0]: ") or "3.0")
            config['min_threshold'] = float(input("最小阈值 (建议0.005-0.02) [默认:0.01]: ") or "0.01")
            config['save_duration'] = int(input("保存时长(秒) [默认:4]: ") or "4")

            custom_dir = input(f"保存目录 [默认:{config['save_directory']}]: ").strip()
            if custom_dir:
                config['save_directory'] = custom_dir
        except ValueError as e:
            print(f"输入无效，使用默认值: {e}")

    # 创建检测器
    if choice == "2":
        detector = AdvancedAudioDetector(**config)
        print("\n使用高级检测模式 (音量+频谱分析)")
    else:
        detector = AudioMutantDetector(**config)
        print("\n使用基础检测模式 (音量检测)")

    # 运行检测
    detector.run()


if __name__ == "__main__":
    main()