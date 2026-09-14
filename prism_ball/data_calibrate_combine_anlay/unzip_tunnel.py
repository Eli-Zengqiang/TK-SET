# -*- coding: utf-8 -*-
"""扫描采集目录, 按设备ID生成解压密码并解压所有 zip 文件。

密码规则:
    md5(设备ID + "tunnelkey")  # 小写

设备ID 读取顺序:
    1) 优先读取 ConfigData-TkSel.cfg 中的 DeviceID
       - 若该密码校验成功, 则不再读取第二个
       - 若校验失败, 打印该 ID 不正确, 继续尝试第 2 个
    2) 从 log.txt 中的 "当前设备ID" 读取
       - 若校验成功, 正常解压
       - 若校验失败, 打印该 ID 不正确并退出

用法:
    python unzip_tunnel.py [采集目录] [输出目录(默认: 目录下 unpacked)]
"""
import re
import sys
import hashlib
import zipfile
from pathlib import Path

from venv.Scripts.activate_this import path

# 默认扫描目录 (可改为任意路径)
DEFAULT_DIR = r"C:\Users\ZHXR\Desktop\test\2026-09-11_11-42-24"

KEY_SUFFIX = "tunnelkey"

CFG_ID_RE = re.compile(r'<Document\s+DeviceID="([^"]+)"')
LOG_ID_RE = re.compile(r"当前设备ID[:：]\s*([A-Za-z0-9]+)")


def make_password(device_id: str) -> str:
    """密码 = md5(设备ID + tunnelkey) 的小写十六进制"""
    return hashlib.md5((device_id + KEY_SUFFIX).encode("utf-8")).hexdigest().lower()


def read_cfg_device_id(folder: Path):
    """从 ConfigData-TkSel.cfg 读取 DeviceID, 找不到返回 None"""
    cfg = folder / "ConfigData-TkSel.cfg"
    if not cfg.exists():
        return None
    m = CFG_ID_RE.search(cfg.read_text(encoding="utf-8", errors="ignore"))
    return m.group(1) if m else None


def read_log_device_id(folder: Path):
    """从 log.txt 的 '当前设备ID' 行读取设备ID, 找不到返回 None"""
    log = folder / "log.txt"
    if not log.exists():
        return None
    m = LOG_ID_RE.search(log.read_text(encoding="utf-8", errors="ignore"))
    return m.group(1) if m else None


def check_password(zips, pwd: str) -> bool:
    """用密码快速校验所有 zip (只读每个文件头部 16 字节即可判定)"""
    pwd_b = pwd.encode("utf-8")
    for zp in zips:
        try:
            with zipfile.ZipFile(zp) as z:
                for info in z.infolist():
                    with z.open(info, pwd=pwd_b) as fp:
                        fp.read(16)
        except (RuntimeError, zipfile.BadZipFile):
            return False
    return True


def extract_all(zips, pwd: str, out_dir: Path) -> int:
    """用密码解压所有 zip 到 out_dir, 返回成功数量"""
    pwd_b = pwd.encode("utf-8")
    ok = 0
    for zp in zips:
        try:
            with zipfile.ZipFile(zp) as z:
                z.extractall(out_dir, pwd=pwd_b)
            ok += 1
            print(f"  解压完成: {zp.name}")
        except (RuntimeError, zipfile.BadZipFile) as e:
            print(f"  解压失败: {zp.name} -> {e}")
    return ok


def main( folder):
    #folder = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(DEFAULT_DIR)
    folder=Path(folder)
    out_dir = Path(sys.argv[2]) if len(sys.argv) > 2 else folder / "unpacked"
    out_dir.mkdir(parents=True, exist_ok=True)

    if not folder.is_dir():
        print(f"目录不存在: {folder}")
        return 1

    zips = sorted(folder.glob("*.zip"), key=lambda p: int(p.stem) if p.stem.isdigit() else p.stem)
    if not zips:
        print(f"目录下没有 zip 文件: {folder}")
        return 1

    print(f"扫描目录: {folder}")
    print(f"找到 zip 文件: {len(zips)} 个")

    # ---------- 第 1 步: 从 cfg 读取 DeviceID ----------
    device_id = read_cfg_device_id(folder)
    if device_id is None:
        print("[警告] 未在 ConfigData-TkSel.cfg 中找到 DeviceID, 跳过第 1 个 ID")
    else:
        password = make_password(device_id)
        print(f"[1] ConfigData-TkSel.cfg 设备ID: {device_id}")
        print(f"    密码(md5): {password}")
        if check_password(zips, password):
            n = extract_all(zips, password, out_dir)
            print(f"完成: 使用 cfg 设备ID 解压成功 {n}/{len(zips)} 个, 输出目录: {out_dir}")
            return 0
        print(f"[1] 该设备ID 不正确: {device_id} (密码 {password} 校验失败)")

    # ---------- 第 2 步: 从 log.txt 读取设备ID ----------
    device_id2 = read_log_device_id(folder)
    if device_id2 is None:
        print("[错误] 未在 log.txt 中找到 当前设备ID, 无法生成密码")
        return 1
    password2 = make_password(device_id2)
    print(f"[2] log.txt 设备ID: {device_id2}")
    print(f"    密码(md5): {password2}")
    if check_password(zips, password2):
        n = extract_all(zips, password2, out_dir)
        print(f"完成: 使用 log.txt 设备ID 解压成功 {n}/{len(zips)} 个, 输出目录: {out_dir}")
        return 0
    print(f"[错误] 该设备ID 也不正确: {device_id2} (密码 {password2} 校验失败)")
    return 1


if __name__ == "__main__":
    folder=r"C:\Users\ZHXR\Desktop\test\2026-09-11_17-56-37/"
    sys.exit(main(folder))