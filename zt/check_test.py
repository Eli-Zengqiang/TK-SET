import os
import librosa
import numpy as np
def load_audio_debug(file_path):
    """
    带调试信息的音频加载函数
    """
    try:
        # 方法1：尝试使用原始采样率
        print("尝试方法1：使用原始采样率...")
        audio, sr = librosa.load(file_path, sr=None, mono=True)
        print("成功！")
        return audio, sr
    except Exception as e1:
        print(f"方法1失败: {e1}")

        try:
            # 方法2：尝试指定采样率
            print("\n尝试方法2：指定采样率22050...")
            audio, sr = librosa.load(file_path, sr=22050, mono=True)
            print("成功！")
            return audio, sr
        except Exception as e2:
            print(f"方法2失败: {e2}")

            try:
                # 方法3：尝试不使用mono
                print("\n尝试方法3：不使用mono...")
                audio, sr = librosa.load(file_path, sr=None, mono=False)
                print("成功！")
                return audio, sr
            except Exception as e3:
                print(f"方法3失败: {e3}")

                try:
                    # 方法4：尝试使用audioread作为后备
                    print("\n尝试方法4：使用audioread...")
                    import audioread
                    with audioread.audio_open(file_path) as f:
                        print(f"格式: {f.format}")
                        print(f"声道数: {f.channels}")
                        print(f"采样率: {f.samplerate}")
                        print(f"时长: {f.duration} 秒")
                    print("audioread成功读取文件信息")

                    # 再尝试用librosa加载
                    audio, sr = librosa.load(file_path, sr=None)
                    print("librosa加载成功！")
                    return audio, sr
                except Exception as e4:
                    print(f"方法4失败: {e4}")
                    return None, None


# 执行调试加载
file_path = r"C:\Users\ZHXR\xwechat_files\wxid_tgmuo001my0d22_7acd\msg\file\2026-03\2.m4a"
audio, sr = load_audio_debug(file_path)