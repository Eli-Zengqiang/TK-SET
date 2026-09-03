# -*- coding: utf-8 -*-
import json
import os
import sys
import time
import traceback
from pathlib import Path

if getattr(sys, "frozen", False):
    # 打包(frozen)环境: 分析脚本与 prism_ball 包放在 exe 旁的 runner_scripts 目录
    _EXE_DIR = Path(sys.executable).resolve().parent
    SCRIPT_DIR = _EXE_DIR / "runner_scripts"
    PROJECT_ROOT = _EXE_DIR / "runner_scripts"
else:
    SCRIPT_DIR = Path(__file__).resolve().parent
    PROJECT_ROOT = SCRIPT_DIR.parents[1]

MARK = "[GUI-MARKER]"
IMAGE_EXTS = {".jpg", ".jpeg", ".png", ".bmp"}

# 强制标准输出/错误以 UTF-8 编码, 保证 GUI 端按 utf-8 解码后中文不乱码
for _stream in (sys.stdout, sys.stderr):
    try:
        _stream.reconfigure(encoding="utf-8")
    except Exception:
        pass

# 供 PyInstaller 静态收集的科学计算库(各分析脚本在运行时导入, 需显式固化)
def _pin_libs():
    import numpy  # noqa: F401
    import scipy  # noqa: F401
    import winpty  # noqa: F401
    import winpty.winpty  # noqa: F401
    try:
        import open3d  # noqa: F401
    except Exception:
        pass
    try:
        import matplotlib  # noqa: F401
        import matplotlib.pyplot  # noqa: F401
    except Exception:
        pass
    try:
        import sklearn  # noqa: F401
    except Exception:
        pass
    try:
        import skspatial  # noqa: F401
        import skspatial.objects  # noqa: F401
    except Exception:
        pass
    import PIL  # noqa: F401

_pin_libs()


def mark(text):
    print(MARK + text, flush=True)


def emit_precision(batch_dir):
    p = Path(batch_dir) / "精度误差.txt"
    if p.exists():
        mark("PRECISION:" + str(p))


def collect_new_images(folders, t0):
    found = []
    for folder in folders:
        root = Path(folder)
        if not root.exists():
            continue
        for f in root.iterdir():
            try:
                if (
                    f.is_file()
                    and f.suffix.lower() in IMAGE_EXTS
                    and f.stat().st_mtime >= t0
                ):
                    found.append(str(f))
            except OSError:
                continue
    return sorted(set(found))


def main():
    cfg = json.loads(Path(sys.argv[1]).read_text(encoding="utf-8"))

    sys.path.insert(0, str(PROJECT_ROOT))
    sys.path.insert(0, str(SCRIPT_DIR))

    from prism_ball.CfgClass import CfgClass
    from prism_ball.data_calibrate_combine_anlay.combine_station_radar_points import (
        combine_Totalstation_points,
    )
    from combine_run_bat_calibrate import run_bat_to_calibrate
    from crop_pointcloud import crop_pointscloude
    from pointcloud_layer_analyze import analyze_pointcloud
    from single_device_test_distance_errorbar import draw_distance_errorbar
    from 联合精度测试 import cacl_error

    data_path = cfg["data_path"]
    bat_path = cfg["bat_path"]
    steps = set(cfg["steps"])

    # 合成exe路径: 覆盖 paths.ReconstructionExe_path
    syn_exe = cfg.get("syn_exe")
    if syn_exe:
        import paths
        paths.ReconstructionExe_path = syn_exe
        print(f"合成exe路径：{syn_exe}", flush=True)

    # 全站仪数据目录(compare根目录)
    ts_dir = cfg.get("ts_dir") or None

    upper_path = Path(data_path)
    datas_folder = str(upper_path.parent) + "/"
    batch_dir = str(upper_path.parent)
    t0 = time.time()

    print(f"父级目录为：{datas_folder}", flush=True)

    hand_angles = None
    if "角度写入" in steps:
        mark("STEP:角度写入")
        combine_Totalstation_points(datas_folder, 2, 1)

    if "标定并写入CFG" in steps:
        mark("STEP:标定并写入CFG")
        hand_angles = run_bat_to_calibrate(bat_path, data_path)
        cfg_path = data_path + "ConfigData-TkSel.cfg"
        sa = CfgClass()
        sa.readFromCFG(cfg_path)
        sa.corret_file_cfg(hand_angles[0], hand_angles[2])
        sa.TotalStationOffsetAngle_cfg(hand_angles[3])
        sa.saveFile(cfg_path)

    datas_folders = None
    if "数据合成" in steps:
        mark("STEP:数据合成")
        datas_folders = combine_Totalstation_points(datas_folder, 2, 2, hand_angles)
        print(datas_folders, flush=True)

    need_folders = bool(
        steps & {"精度计算", "误差棒图绘制", "点云截取", "点云分层分析"}
    )
    if need_folders and not datas_folders:
        print("未获得数据文件夹列表，请先勾选并执行【数据合成】步骤", flush=True)
        sys.exit(2)

    if "精度计算" in steps:
        mark("STEP:精度计算")
        cacl_error(datas_folders, fold=ts_dir)
        emit_precision(batch_dir)

    if "误差棒图绘制" in steps:
        mark("STEP:误差棒图绘制")
        draw_distance_errorbar(datas_folders, total_data=ts_dir)
        for p in collect_new_images([batch_dir], t0):
            mark("IMAGE:" + p)

    if "点云截取" in steps:
        mark("STEP:点云截取")
        crop_pointscloude(datas_folders[3])

    if "点云分层分析" in steps:
        mark("STEP:点云分层分析")
        analyze_pointcloud(datas_folders[3])
        emit_precision(batch_dir)
        for p in collect_new_images([batch_dir], t0):
            mark("IMAGE:" + p)

    mark("DONE:0")


if __name__ == "__main__":
    try:
        main()
    except SystemExit:
        raise
    except Exception:
        traceback.print_exc()
        mark("DONE:1")
