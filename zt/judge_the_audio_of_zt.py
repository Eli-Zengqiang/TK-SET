
import pyaudio
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
from collections import deque
import threading

#实时音频可视化
class VisualAudioMonitor:
    def __init__(self, rate=16000, chunk=1024):
        self.rate = rate
        self.chunk = chunk
        self.audio = pyaudio.PyAudio()

        # 数据缓冲区
        self.audio_buffer = deque(maxlen=rate * 2)  # 2秒的音频
        self.volume_history = deque(maxlen=100)
        self.spectrum_buffer = deque(maxlen=10)

        # 设置绘图
        plt.style.use('dark_background')
        self.fig, (self.ax1, self.ax2, self.ax3) = plt.subplots(3, 1, figsize=(10, 8))

        # 初始化绘图元素
        self.wave_line, = self.ax1.plot([], [], 'c-', linewidth=1)
        self.volume_line, = self.ax2.plot([], [], 'g-', linewidth=1)
        self.spectrum_line, = self.ax3.plot([], [], 'r-', linewidth=1)

        self.threshold_line = self.ax2.axhline(y=0, color='r', linestyle='--', alpha=0.7)

    def setup_plots(self):
        """设置图表"""
        # 波形图
        self.ax1.set_xlim(0, self.rate // 10)  # 显示100ms
        self.ax1.set_ylim(-32768, 32768)
        self.ax1.set_title('实时波形')
        self.ax1.set_xlabel('采样点')
        self.ax1.set_ylabel('振幅')

        # 音量历史
        self.ax2.set_xlim(0, 100)
        self.ax2.set_ylim(0, 5000)
        self.ax2.set_title('音量变化')
        self.ax2.set_xlabel('时间')
        self.ax2.set_ylabel('RMS')

        # 频谱
        self.ax3.set_xlim(0, 8000)  # 显示8kHz
        self.ax3.set_ylim(0, 100)
        self.ax3.set_title('实时频谱')
        self.ax3.set_xlabel('频率 (Hz)')
        self.ax3.set_ylabel('幅度')

        plt.tight_layout()

    def update_plot(self, frame):
        """更新绘图"""
        if len(self.audio_buffer) > 0:
            # 更新波形
            recent_data = list(self.audio_buffer)[-self.rate // 10:]  # 最近的100ms
            if recent_data:
                self.wave_line.set_data(range(len(recent_data)), recent_data)

                # 动态调整Y轴
                max_amp = max(abs(min(recent_data)), abs(max(recent_data)))
                self.ax1.set_ylim(-max_amp * 1.2, max_amp * 1.2)

            # 更新音量历史
            if self.volume_history:
                self.volume_line.set_data(range(len(self.volume_history)),
                                          list(self.volume_history))

                # 计算阈值
                avg_volume = np.mean(list(self.volume_history))
                threshold = avg_volume * 2.5
                self.threshold_line.set_ydata([threshold, threshold])

                # 检测突变
                current_volume = self.volume_history[-1]
                if current_volume > threshold:
                    self.ax2.set_title(f'音量变化 (检测到突变! {current_volume:.0f} > {threshold:.0f})')
                    self.threshold_line.set_color('r')
                else:
                    self.ax2.set_title('音量变化')
                    self.threshold_line.set_color('orange')

            # 更新频谱
            if len(self.audio_buffer) >= self.chunk:
                data = np.array(list(self.audio_buffer)[-self.chunk:])

                # 计算频谱
                windowed = data * np.hanning(len(data))
                fft = np.fft.rfft(windowed)
                magnitude = np.abs(fft)
                freq = np.fft.rfftfreq(len(data), 1 / self.rate)

                # 只显示有意义的频率
                mask = freq <= 8000
                self.spectrum_line.set_data(freq[mask], magnitude[mask])

        return self.wave_line, self.volume_line, self.spectrum_line

    def audio_callback(self, in_data, frame_count, time_info, status):
        """音频回调函数"""
        audio_data = np.frombuffer(in_data, dtype=np.int16)

        # 添加到缓冲区
        self.audio_buffer.extend(audio_data)

        # 计算RMS音量
        rms = np.sqrt(np.mean(audio_data.astype(np.float32) ** 2))
        self.volume_history.append(rms)

        return (in_data, pyaudio.paContinue)

    def start_monitoring(self):
        """开始监控"""
        self.setup_plots()

        # 打开音频流
        stream = self.audio.open(
            format=pyaudio.paInt16,
            channels=1,
            rate=self.rate,
            input=True,
            frames_per_buffer=self.chunk,
            stream_callback=self.audio_callback
        )

        # 启动动画
        anim = FuncAnimation(self.fig, self.update_plot,
                             interval=50, blit=True, cache_frame_data=False)

        print("可视化音频监控启动... 关闭窗口停止")
        plt.show()

        stream.stop_stream()
        stream.close()
        self.audio.terminate()


# 使用示例
if __name__ == "__main__":
    monitor = VisualAudioMonitor()
    monitor.start_monitoring()