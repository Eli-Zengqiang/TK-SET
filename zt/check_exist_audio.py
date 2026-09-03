#
# import numpy as np
# import librosa
# import soundfile as sf
# import matplotlib.pyplot as plt
# from scipy import signal
# import warnings
#
# warnings.filterwarnings('ignore')
# import os
# import subprocess
# import tempfile
#
#
# def check_audio_format(audio_path):
#     """检查音频文件格式并返回相关信息"""
#     file_ext = os.path.splitext(audio_path)[1].lower()
#     print(f"文件格式: {file_ext}")
#
#     # 检查文件大小
#     file_size = os.path.getsize(audio_path) / (1024 * 1024)  # MB
#     print(f"文件大小: {file_size:.2f} MB")
#
#     return file_ext, file_size
#
#
# def convert_m4a_to_wav(m4a_path):
#     """将m4a转换为wav格式（使用ffmpeg）"""
#     try:
#         # 创建临时文件
#         temp_wav = tempfile.NamedTemporaryFile(suffix='.wav', delete=False)
#         temp_wav.close()
#
#         # 使用ffmpeg转换
#         cmd = ['ffmpeg', '-i', m4a_path, '-acodec', 'pcm_s16le', '-ar', '44100', '-ac', '1', temp_wav.name, '-y']
#         result = subprocess.run(cmd, capture_output=True, text=True)
#
#         if result.returncode == 0:
#             print("成功将m4a转换为wav格式")
#             return temp_wav.name
#         else:
#             print(f"ffmpeg转换失败: {result.stderr}")
#             return None
#     except Exception as e:
#         print(f"转换过程出错: {e}")
#         return None
#
#
# def load_audio_robust(audio_path):
#     """
#     健壮的音频加载函数，支持多种格式
#     """
#     audio = None
#     sr = None
#
#     # 方法1: 使用librosa（支持多种格式，但可能需要额外库）
#     try:
#         print("尝试使用librosa加载...")
#         audio, sr = librosa.load(audio_path, sr=None, mono=True)
#         print(f"librosa加载成功: {sr} Hz, {len(audio)} 样本")
#         return audio, sr
#     except Exception as e:
#         print(f"librosa加载失败: {e}")
#
#     # 方法2: 使用soundfile（支持wav, flac, ogg等）
#     try:
#         print("尝试使用soundfile加载...")
#         audio, sr = sf.read(audio_path)
#         # 如果是立体声，转换为单声道
#         if len(audio.shape) > 1:
#             audio = np.mean(audio, axis=1)
#         print(f"soundfile加载成功: {sr} Hz, {len(audio)} 样本")
#         return audio, sr
#     except Exception as e:
#         print(f"soundfile加载失败: {e}")
#
#     # 方法3: 对于m4a文件，尝试使用ffmpeg转换
#     file_ext = os.path.splitext(audio_path)[1].lower()
#     if file_ext == '.m4a':
#         print("检测到m4a格式，尝试使用ffmpeg转换...")
#         temp_wav = convert_m4a_to_wav(audio_path)
#         if temp_wav:
#             try:
#                 audio, sr = sf.read(temp_wav)
#                 if len(audio.shape) > 1:
#                     audio = np.mean(audio, axis=1)
#                 print(f"ffmpeg转换后加载成功: {sr} Hz, {len(audio)} 样本")
#                 # 删除临时文件
#                 os.unlink(temp_wav)
#                 return audio, sr
#             except Exception as e:
#                 print(f"转换后加载失败: {e}")
#                 if os.path.exists(temp_wav):
#                     os.unlink(temp_wav)
#
#     return None, None
#
#
# def detect_audio_anomalies(audio_path, threshold_multiplier=3.0, window_size=2048, hop_length=512):
#     """
#     检测音频文件中的声音突变
#     """
#
#     # 加载音频文件
#     print(f"正在加载音频文件: {audio_path}")
#
#     # 检查文件格式
#     file_ext, file_size = check_audio_format(audio_path)
#
#     # 使用健壮的加载函数
#     audio, sr = load_audio_robust(audio_path)
#
#     if audio is None or sr is None:
#         print("所有加载方法都失败了！")
#         print("\n可能的解决方案:")
#         print("1. 安装ffmpeg: https://ffmpeg.org/download.html")
#         print("2. 将文件转换为wav格式后再试")
#         print("3. 检查文件是否损坏")
#         return None, None, None
#
#     print(f"\n音频信息:")
#     print(f"- 采样率: {sr} Hz")
#     print(f"- 时长: {len(audio) / sr:.2f} 秒")
#     print(f"- 样本数: {len(audio)}")
#     print(f"- 最大振幅: {np.max(np.abs(audio)):.4f}")
#     print(f"- 平均振幅: {np.mean(np.abs(audio)):.4f}")
#
#     # 1. 计算短时能量
#     energy = librosa.feature.rms(y=audio, frame_length=window_size, hop_length=hop_length)[0]
#
#     # 2. 计算能量的一阶差分（能量变化率）
#     energy_diff = np.abs(np.diff(energy, prepend=energy[0]))
#
#     # 3. 检测突变
#     # 方法1：基于能量变化率
#     energy_diff_mean = np.mean(energy_diff)
#     energy_diff_std = np.std(energy_diff)
#     energy_threshold = energy_diff_mean + threshold_multiplier * energy_diff_std
#
#     # 方法2：基于能量绝对值
#     energy_mean = np.mean(energy)
#     energy_std = np.std(energy)
#     energy_abs_threshold = energy_mean + threshold_multiplier * energy_std
#
#     # 找到突变位置
#     anomaly_indices_energy = np.where(energy_diff > energy_threshold)[0]
#     anomaly_indices_abs = np.where(energy > energy_abs_threshold)[0]
#
#     # 合并两种检测结果
#     all_anomalies = np.unique(np.concatenate([anomaly_indices_energy, anomaly_indices_abs]))
#
#     # 计算突变分数
#     anomaly_scores = np.zeros_like(energy)
#     if len(anomaly_indices_energy) > 0:
#         anomaly_scores[anomaly_indices_energy] = energy_diff[anomaly_indices_energy] / energy_threshold
#     if len(anomaly_indices_abs) > 0:
#         anomaly_scores[anomaly_indices_abs] = energy[anomaly_indices_abs] / energy_abs_threshold
#
#     # 将帧索引转换为时间
#     anomaly_times = librosa.frames_to_time(all_anomalies, sr=sr, hop_length=hop_length)
#
#     # 创建结果字典
#     results = {
#         'anomaly_times': anomaly_times,
#         'anomaly_scores': anomaly_scores,
#         'energy': energy,
#         'energy_diff': energy_diff,
#         'energy_threshold': energy_threshold,
#         'energy_abs_threshold': energy_abs_threshold,
#         'frame_times': librosa.frames_to_time(np.arange(len(energy)), sr=sr, hop_length=hop_length)
#     }
#
#     return results, audio, sr
#
#
# def visualize_anomalies(results, audio, sr, audio_path):
#     """
#     可视化音频和检测到的突变
#     """
#     if results is None or audio is None:
#         print("没有数据可可视化")
#         return
#
#     fig, axes = plt.subplots(3, 1, figsize=(14, 10))
#
#     # 绘制原始波形
#     time = np.linspace(0, len(audio) / sr, len(audio))
#     axes[0].plot(time, audio, color='blue', alpha=0.7, linewidth=0.5)
#     axes[0].set_title('原始音频波形', fontsize=12)
#     axes[0].set_xlabel('时间 (秒)')
#     axes[0].set_ylabel('振幅')
#     axes[0].grid(True, alpha=0.3)
#
#     # 绘制能量和突变点
#     axes[1].plot(results['frame_times'], results['energy'], color='green', label='短时能量')
#     axes[1].axhline(y=results['energy_abs_threshold'], color='red', linestyle='--',
#                     label=f'能量阈值 ({results["energy_abs_threshold"]:.3f})')
#
#     # 标记突变点
#     if len(results['anomaly_times']) > 0:
#         for t in results['anomaly_times']:
#             axes[1].axvline(x=t, color='red', alpha=0.5, linestyle=':', linewidth=1)
#
#     axes[1].set_title('短时能量及突变检测', fontsize=12)
#     axes[1].set_xlabel('时间 (秒)')
#     axes[1].set_ylabel('能量')
#     axes[1].legend()
#     axes[1].grid(True, alpha=0.3)
#
#     # 绘制能量变化率
#     axes[2].plot(results['frame_times'], results['energy_diff'], color='orange', label='能量变化率')
#     axes[2].axhline(y=results['energy_threshold'], color='red', linestyle='--',
#                     label=f'变化率阈值 ({results["energy_threshold"]:.3f})')
#     axes[2].set_title('能量变化率', fontsize=12)
#     axes[2].set_xlabel('时间 (秒)')
#     axes[2].set_ylabel('变化率')
#     axes[2].legend()
#     axes[2].grid(True, alpha=0.3)
#
#     plt.suptitle(f'音频突变检测结果: {os.path.basename(audio_path)}', fontsize=14)
#     plt.tight_layout()
#     plt.show()
#
#
# def analyze_audio_anomalies(audio_path, threshold_multiplier=3.0):
#     """
#     主分析函数
#     """
#     print("=" * 60)
#     print(f"开始分析音频文件: {audio_path}")
#     print("=" * 60)
#
#     # 检查文件是否存在
#     if not os.path.exists(audio_path):
#         print(f"错误: 文件不存在 - {audio_path}")
#         return None
#
#     # 检测突变
#     results, audio, sr = detect_audio_anomalies(audio_path, threshold_multiplier)
#
#     if results is None or audio is None:
#         print("分析失败！")
#         print("\n建议:")
#         print("1. 安装ffmpeg: pip install ffmpeg-python 或直接下载ffmpeg")
#         print("2. 使用在线工具将文件转换为wav格式")
#         print("3. 检查文件是否完整")
#         return None
#
#     # 打印检测结果
#     anomaly_times = results['anomaly_times']
#
#     print(f"\n检测结果:")
#     print(f"- 阈值倍数: {threshold_multiplier}")
#     print(f"- 能量阈值: {results['energy_abs_threshold']:.4f}")
#     print(f"- 变化率阈值: {results['energy_threshold']:.4f}")
#     print(f"- 检测到的突变数量: {len(anomaly_times)}")
#
#     if len(anomaly_times) > 0:
#         print("\n突变位置（秒）:")
#         for i, t in enumerate(anomaly_times[:10]):  # 只显示前10个
#             print(f"  {i + 1}. {t:.3f} 秒")
#
#         if len(anomaly_times) > 10:
#             print(f"  ... 还有 {len(anomaly_times) - 10} 个突变点")
#
#         # 计算突变严重程度
#         valid_scores = results['anomaly_scores'][results['anomaly_scores'] > 0]
#         if len(valid_scores) > 0:
#             max_score = np.max(valid_scores)
#             avg_score = np.mean(valid_scores)
#
#             print(f"\n突变统计:")
#             print(f"- 最大突变分数: {max_score:.2f}")
#             print(f"- 平均突变分数: {avg_score:.2f}")
#
#             # 评估音频质量
#             if max_score > 5:
#                 quality = "非常差 - 存在极端突变"
#             elif max_score > 3:
#                 quality = "较差 - 存在明显突变"
#             elif max_score > 2:
#                 quality = "一般 - 存在一些突变"
#             else:
#                 quality = "良好 - 没有明显突变"
#
#             print(f"- 音频质量评估: {quality}")
#     else:
#         print("\n未检测到明显的声音突变！")
#         print("- 音频质量评估: 优秀 - 音频平稳")
#
#     # 可视化结果
#     visualize_anomalies(results, audio, sr, audio_path)
#
#     return results
#
#
# # 使用示例
# if __name__ == "__main__":
#     # 请替换为你的音频文件路径
#     audio_file = r"C:\Users\ZHXR\xwechat_files\wxid_tgmuo001my0d22_7acd\msg\file\2026-03\2.mp3"
#
#     # 检查文件是否存在
#     if os.path.exists(audio_file):
#         # 分析音频突变
#         results = analyze_audio_anomalies(audio_file, threshold_multiplier=3.0)
#
#         # 如果需要导出突变位置到文件
#         if results is not None and len(results['anomaly_times']) > 0:
#             output_file = "anomaly_times.txt"
#             with open(output_file, 'w', encoding='utf-8') as f:
#                 for t in results['anomaly_times']:
#                     f.write(f"{t:.3f}\n")
#             print(f"\n突变位置已保存到: {output_file}")
#     else:
#         print(f"文件不存在: {audio_file}")


import numpy as np
import librosa
import matplotlib.pyplot as plt
from scipy import signal
import warnings

warnings.filterwarnings('ignore')


def load_audio(file_path):
    """
    加载音频文件
    """
    try:
        # 加载音频文件，sr=None表示保持原始采样率
        audio, sr = librosa.load(file_path, sr=None, mono=True)
        print(f"音频文件加载成功！")
        print(f"采样率: {sr} Hz")
        print(f"音频时长: {len(audio) / sr:.2f} 秒")
        print(f"音频样本数: {len(audio)}")
        return audio, sr
    except Exception as e:
        print(f"加载音频文件失败: {e}")
        return None, None


def detect_sound_sudden_changes(audio, sr, threshold_multiplier=3.0, window_size=0.05):
    """
    检测音频中的声音突变

    参数:
    - audio: 音频数据
    - sr: 采样率
    - threshold_multiplier: 阈值倍数，用于判断突变
    - window_size: 滑动窗口大小（秒）

    返回:
    -突变点位置和相关信息
    """

    # 计算短时能量
    frame_length = int(window_size * sr)
    hop_length = frame_length // 4

    # 计算RMS能量
    rms = librosa.feature.rms(y=audio, frame_length=frame_length, hop_length=hop_length)[0]

    # 计算能量变化率（一阶差分）
    energy_diff = np.diff(rms)

    # 计算能量变化率的绝对值
    abs_energy_diff = np.abs(energy_diff)

    # 设置检测阈值
    threshold = np.mean(abs_energy_diff) + threshold_multiplier * np.std(abs_energy_diff)

    # 找到突变点（超过阈值的位置）
    sudden_changes = np.where(abs_energy_diff > threshold)[0]

    # 将帧索引转换为时间
    times = librosa.frames_to_time(sudden_changes, sr=sr, hop_length=hop_length)

    # 获取突变点的能量值
    change_values = abs_energy_diff[sudden_changes]

    return {
        'times': times,
        'values': change_values,
        'threshold': threshold,
        'rms': rms,
        'energy_diff': energy_diff,
        'times_all': librosa.frames_to_time(np.arange(len(rms)), sr=sr, hop_length=hop_length)
    }


def detect_clipping(audio, threshold=0.99):
    """
    检测音频削波（爆音）
    """
    # 检测接近最大值的样本
    max_amplitude = np.max(np.abs(audio))
    clipping_samples = np.where(np.abs(audio) > threshold)[0]

    if len(clipping_samples) > 0:
        clipping_ratio = len(clipping_samples) / len(audio) * 100
        return {
            'has_clipping': True,
            'clipping_samples': clipping_samples,
            'clipping_ratio': clipping_ratio,
            'max_amplitude': max_amplitude
        }
    else:
        return {
            'has_clipping': False,
            'clipping_ratio': 0,
            'max_amplitude': max_amplitude
        }


def plot_analysis(audio, sr, changes_result, clipping_result):
    """
    可视化分析结果
    """
    fig, axes = plt.subplots(3, 1, figsize=(12, 10))

    # 时间轴
    time = np.arange(len(audio)) / sr

    # 1. 原始波形
    axes[0].plot(time, audio, color='blue', alpha=0.7, linewidth=0.5)
    axes[0].set_title('原始音频波形', fontsize=12)
    axes[0].set_xlabel('时间 (秒)')
    axes[0].set_ylabel('振幅')
    axes[0].grid(True, alpha=0.3)

    # 标记削波位置
    if clipping_result['has_clipping']:
        clip_times = clipping_result['clipping_samples'] / sr
        axes[0].scatter(clip_times, audio[clipping_result['clipping_samples']],
                        color='red', s=10, alpha=0.5, label='削波/爆音')
        axes[0].legend()

    # 2. RMS能量和突变点
    axes[1].plot(changes_result['times_all'], changes_result['rms'],
                 color='green', alpha=0.7, label='RMS能量')

    # 标记突变点
    if len(changes_result['times']) > 0:
        axes[1].scatter(changes_result['times'],
                        changes_result['rms'][changes_result['times'] // (
                                    changes_result['times_all'][1] - changes_result['times_all'][0])],
                        color='red', s=50, label='能量突变点', zorder=5)

    axes[1].axhline(y=np.mean(changes_result['rms']), color='orange',
                    linestyle='--', alpha=0.5, label='平均能量')
    axes[1].set_title('RMS能量分析', fontsize=12)
    axes[1].set_xlabel('时间 (秒)')
    axes[1].set_ylabel('能量')
    axes[1].legend()
    axes[1].grid(True, alpha=0.3)

    # 3. 能量变化率
    axes[2].plot(changes_result['times_all'][1:], changes_result['energy_diff'],
                 color='purple', alpha=0.7, label='能量变化率')
    axes[2].axhline(y=changes_result['threshold'], color='red',
                    linestyle='--', label='突变阈值')
    axes[2].axhline(y=-changes_result['threshold'], color='red',
                    linestyle='--')
    axes[2].set_title('能量变化率分析', fontsize=12)
    axes[2].set_xlabel('时间 (秒)')
    axes[2].set_ylabel('变化率')
    axes[2].legend()
    axes[2].grid(True, alpha=0.3)

    plt.tight_layout()
    plt.show()


def print_results(changes_result, clipping_result):
    """
    打印检测结果
    """
    print("\n" + "=" * 50)
    print("声音突变检测结果")
    print("=" * 50)

    # 削波检测结果
    print(f"\n【削波/爆音检测】")
    print(f"最大振幅: {clipping_result['max_amplitude']:.4f}")
    if clipping_result['has_clipping']:
        print(f"发现削波! 削波样本比例: {clipping_result['clipping_ratio']:.3f}%")
        print(f"削波样本数量: {len(clipping_result['clipping_samples'])}")
    else:
        print("未检测到明显的削波现象")

    # 能量突变检测结果
    print(f"\n【能量突变检测】")
    print(f"检测阈值: {changes_result['threshold']:.4f}")

    if len(changes_result['times']) > 0:
        print(f"发现 {len(changes_result['times'])} 处能量突变点:")
        for i, (time, value) in enumerate(zip(changes_result['times'], changes_result['values'])):
            print(f"  突变点 {i + 1}: 时间={time:.3f}秒, 变化率={value:.4f}")
    else:
        print("未检测到明显的能量突变点")


# 主程序
def main():
    # 音频文件路径（请替换为您的音频文件路径）
    audio_file = r"C:\Users\ZHXR\xwechat_files\wxid_tgmuo001my0d22_7acd\msg\file\2026-03\2.m4a"  # 支持 .wav, .mp3, .m4a 等格式

    # 1. 加载音频
    audio, sr = load_audio(audio_file)
    if audio is None:
        return

    # 2. 检测削波
    clipping_result = detect_clipping(audio)

    # 3. 检测能量突变
    changes_result = detect_sound_sudden_changes(
        audio,
        sr,
        threshold_multiplier=3.0,  # 可以调整这个值来改变检测灵敏度
        window_size=0.05  # 窗口大小（秒）
    )

    # 4. 打印结果
    print_results(changes_result, clipping_result)

    # 5. 可视化
    plot_analysis(audio, sr, changes_result, clipping_result)


if __name__ == "__main__":
    main()