# -*- coding: utf-8 -*-
import json
import os
import re
import subprocess
import sys
import tempfile
import threading
from pathlib import Path

from PyQt5.QtCore import QSettings, Qt, QThread, QTimer, pyqtSignal
from PyQt5.QtGui import QColor, QFont, QIcon, QPixmap, QTextCursor, QTextFormat
from PyQt5.QtWidgets import (
    QApplication,
    QCheckBox,
    QDialog,
    QFileDialog,
    QGridLayout,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QListWidget,
    QListWidgetItem,
    QMessageBox,
    QPlainTextEdit,
    QPushButton,
    QSplitter,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)
from PyQt5.QtCore import QSize

SCRIPT_DIR = Path(__file__).resolve().parent
RUNNER_PATH = SCRIPT_DIR / "calib_runner.py"
PROJECT_ROOT = SCRIPT_DIR.parents[1]

DEFAULT_DATA_PATH = r"G:\TK-set\2.1data\20260807\b524\2026-08-07_10-45-44/"
DEFAULT_BAT_PATH = (
    r"C:\Users\ZHXR\Desktop\com_tool\2.1data\2.1cloud_combine_tool"
    r"\标定-0516\180标定-0.5\智隧慧眼2.1标定.bat"
)

# 从 paths.py / 联合精度测试.py 读取默认路径(与原本位置保持一致)
def _read_default(path_file, pat):
    try:
        for line in Path(path_file).read_text(encoding="utf-8").splitlines():
            m = re.search(pat, line)
            if m:
                return m.group(1)
    except Exception:
        pass
    return None

DEFAULT_SYN_EXE = _read_default(
    SCRIPT_DIR / "paths.py",
    r'ReconstructionExe_path\s*=\s*r?"([^"]+)"',
) or r"C:\Users\ZHXR\Desktop\com_tool\2.1data\tool_or_script\标定工具v1.1_20240522\main\exe\ScanAndProcess-270.exe"

DEFAULT_TS_DATA_DIR = _read_default(
    SCRIPT_DIR / "联合精度测试.py",
    r'fold\s*=\s*r?"([^"]+)"',
) or r"C:\Users\ZHXR\Desktop\com_tool\2.1data\testbd\全站仪数据\compare/"

STEP_WRITE_ANGLE = "角度写入"
STEP_CALIBRATE = "标定并写入CFG"
STEP_COMBINE = "数据合成"
STEP_PRECISION = "精度计算"
STEP_ERRORBAR = "误差棒图绘制"
STEP_CROP = "点云截取"
STEP_LAYER = "点云分层分析"

ALL_STEPS = [
    STEP_WRITE_ANGLE,
    STEP_CALIBRATE,
    STEP_COMBINE,
    STEP_PRECISION,
    STEP_ERRORBAR,
    STEP_CROP,
    STEP_LAYER,
]

MARK = "[GUI-MARKER]"
LOG_MAX_BLOCKS = 3000
PENDING_CAP = 6000

# 标定合成分析报告版本号
REPORT_VERSION = "V1.0.0.1"

# 测试结果判定:
#   某位置"平均误差(位置精度)"或"标准差"任一超过该阈值, 该位置即判不通过;
#   某楼内不通过位置数量达到此数量即判"未通过"(未达到则"通过")
PRECISION_THRESHOLD = 0.01
PRECISION_FAIL_COUNT = 2

# 分层结论判定: 存在分层 且 层间距均值超过该阈值即判"未通过"
LAYER_GAP_THRESHOLD = 0.015

# 楼栋显示名称 -> 精度文件中该楼的所有别名(用于定位段落)
BUILDINGS = [
    ("0号楼", ["0号楼"]),
    ("一楼", ["1楼", "一楼"]),
    ("二楼", ["2楼", "二楼", "创新大厦"]),
]


class ScriptProcess(QThread):
    precision_ready = pyqtSignal(str)
    images_ready = pyqtSignal(list)
    step_changed = pyqtSignal(str)
    run_finished = pyqtSignal(bool)

    def __init__(self, cfg, parent=None):
        super().__init__(parent)
        self.cfg = cfg
        self.proc = None
        self._stop = False
        self._lock = threading.Lock()
        self._pending = []

    def drain_text(self):
        with self._lock:
            if not self._pending:
                return ""
            chunk = "".join(self._pending)
            self._pending.clear()
        return chunk

    def request_stop(self):
        self._stop = True
        proc = self.proc
        if proc and proc.poll() is None:
            try:
                subprocess.run(
                    ["taskkill", "/T", "/F", "/PID", str(proc.pid)],
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL,
                )
            except Exception:
                try:
                    proc.kill()
                except Exception:
                    pass

    def _runner_command(self, cfg_file):
        # 打包(Frozen)环境下: 主 exe 同目录下的 calib_runner.exe
        if getattr(sys, "frozen", False):
            runner_exe = Path(sys.executable).resolve().parent / "calib_runner.exe"
            if runner_exe.exists():
                return [str(runner_exe), str(cfg_file)]
        # 开发态/回退: 用当前 Python 解释器运行 calib_runner.py
        return [sys.executable, str(RUNNER_PATH), str(cfg_file)]

    def run(self):
        cfg_file = Path(tempfile.gettempdir()) / "calib_gui_config.json"
        cfg_file.write_text(
            json.dumps(self.cfg, ensure_ascii=False, indent=1),
            encoding="utf-8",
        )
        env = os.environ.copy()
        env["PYTHONUNBUFFERED"] = "1"
        env["PYTHONIOENCODING"] = "utf-8"
        creationflags = getattr(subprocess, "CREATE_NO_WINDOW", 0)
        ok = False
        try:
            runner_cmd = self._runner_command(cfg_file)
            self.proc = subprocess.Popen(
                runner_cmd,
                cwd=str(SCRIPT_DIR),
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                encoding="utf-8",
                errors="replace",
                bufsize=1,
                env=env,
                creationflags=creationflags,
            )
            for raw in self.proc.stdout:
                if self._stop:
                    break
                line = raw.rstrip("\r\n")
                if not line:
                    with self._lock:
                        self._pending.append("\n")
                    continue
                if line.startswith(MARK):
                    payload = line[len(MARK):]
                    kind, _, value = payload.partition(":")
                    if kind == "PRECISION":
                        p = Path(value)
                        if p.exists():
                            try:
                                self.precision_ready.emit(
                                    p.read_text(encoding="utf-8")
                                )
                            except OSError:
                                pass
                    elif kind == "IMAGE":
                        self.images_ready.emit([value])
                    elif kind == "STEP":
                        self.step_changed.emit(value)
                    elif kind == "DONE":
                        ok = value == "0"
                        break
                else:
                    with self._lock:
                        self._pending.append(line + "\n")
                        if len(self._pending) > PENDING_CAP:
                            del self._pending[: len(self._pending) // 2]
            try:
                self.proc.wait(timeout=5)
            except Exception:
                pass
        except Exception as exc:
            with self._lock:
                self._pending.append(f"\n[异常] {exc}\n")
            ok = False
        ok = ok and not self._stop
        self.run_finished.emit(ok)


class ImageViewer(QDialog):
    def __init__(self, img_path, parent=None):
        super().__init__(parent)
        self.setWindowTitle(Path(img_path).name)
        layout = QVBoxLayout(self)
        label = QLabel()
        pixmap = QPixmap(img_path)
        screen = QApplication.primaryScreen().availableGeometry()
        scaled = pixmap.scaled(
            screen.width() - 120,
            screen.height() - 120,
            Qt.KeepAspectRatio,
            Qt.SmoothTransformation,
        )
        label.setPixmap(scaled)
        layout.addWidget(label)


class MainWindow(QWidget):
    CFG_KEYS = [
        ("data", "data_path"),
        ("bat", "bat_path"),
        ("syn_exe", "syn_exe"),
        ("ts_dir", "ts_dir"),
    ]

    def __init__(self):
        super().__init__()
        self.worker = None
        self._user_stopped = False
        self.settings = QSettings(str(SCRIPT_DIR / "gui_config.ini"), QSettings.IniFormat)
        self._build_ui()

        self.log_timer = QTimer(self)
        self.log_timer.setInterval(150)
        self.log_timer.timeout.connect(self.flush_log)

    def _build_ui(self):
        self.setWindowTitle("标定合成分析工具")
        self.resize(1360, 800)

        root_layout = QHBoxLayout(self)
        root_layout.addWidget(self._build_left_panel())
        root_layout.addWidget(self._build_middle_panel(), 1)
        root_layout.addWidget(self._build_right_panel())

    def _build_left_panel(self):
        panel = QWidget()
        panel.setFixedWidth(110)
        layout = QVBoxLayout(panel)

        self.ver_label = QLabel(REPORT_VERSION)
        self.ver_label.setAlignment(Qt.AlignCenter)
        self.ver_label.setStyleSheet("font-size:13px;font-weight:bold;color:#1565c0;")

        self.btn_about = QPushButton("关于")
        self.btn_about.setFixedHeight(24)
        self.btn_about.setCursor(Qt.PointingHandCursor)
        self.btn_about.setStyleSheet(
            "font-size:11px;background:#eceff1;color:#37474f;"
            "border:1px solid #b0bec5;border-radius:4px;"
        )
        self.btn_about.clicked.connect(self.show_about)

        ver_row = QHBoxLayout()
        ver_row.addWidget(self.ver_label)
        ver_row.addWidget(self.btn_about)

        self.btn_start = QPushButton("开始")
        self.btn_start.setFixedHeight(70)
        self.btn_start.setStyleSheet(
            "font-size:18px;font-weight:bold;background:#2e7d32;"
            "color:white;border:none;border-radius:8px;"
        )
        self.btn_start.clicked.connect(self.start_run)

        self.btn_stop = QPushButton("结束")
        self.btn_stop.setFixedHeight(52)
        self.btn_stop.setEnabled(False)
        self.btn_stop.setStyleSheet(
            "font-size:16px;font-weight:bold;background:#c62828;"
            "color:white;border:none;border-radius:8px;"
        )
        self.btn_stop.clicked.connect(self.stop_run)

        self.lbl_status = QLabel("就绪")
        self.lbl_status.setAlignment(Qt.AlignCenter)
        self.lbl_status.setWordWrap(True)
        self.lbl_status.setStyleSheet("color:#555;font-size:12px;")

        layout.addLayout(ver_row)
        layout.addStretch(2)
        layout.addWidget(self.btn_start)
        layout.addSpacing(16)
        layout.addWidget(self.btn_stop)
        layout.addStretch(1)
        layout.addWidget(self.lbl_status)
        layout.addStretch(2)
        return panel

    def _build_middle_panel(self):
        splitter = QSplitter(Qt.Vertical)

        group_log = QGroupBox("运行内容")
        log_layout = QVBoxLayout(group_log)
        self.log_view = QPlainTextEdit()
        self.log_view.setReadOnly(True)
        self.log_view.setMaximumBlockCount(LOG_MAX_BLOCKS)
        self.log_view.setFont(QFont("Consolas", 9))
        log_layout.addWidget(self.log_view)

        group_precision = QGroupBox("精度输出")
        precision_layout = QVBoxLayout(group_precision)
        self.precision_view = QPlainTextEdit()
        self.precision_view.setReadOnly(True)
        self.precision_view.setFont(QFont("Consolas", 10))
        precision_layout.addWidget(self.precision_view)

        group_images = QGroupBox("图片展示（双击查看大图）")
        images_layout = QVBoxLayout(group_images)
        self.image_list = QListWidget()
        self.image_list.setViewMode(QListWidget.IconMode)
        self.image_list.setIconSize(QSize(160, 120))
        self.image_list.setResizeMode(QListWidget.Adjust)
        self.image_list.setSpacing(10)
        self.image_list.itemDoubleClicked.connect(self.open_image_viewer)
        images_layout.addWidget(self.image_list)

        splitter.addWidget(group_log)
        splitter.addWidget(group_precision)
        splitter.addWidget(group_images)
        splitter.setSizes([380, 280, 280])
        return splitter

    def _build_right_panel(self):
        panel = QWidget()
        panel.setFixedWidth(330)
        layout = QVBoxLayout(panel)

        box_files = QGroupBox("文件配置")
        files_layout = QGridLayout(box_files)

        lbl_data = QLabel("数据文件夹-0号楼")
        self.edit_data = QLineEdit(
            self.settings.value("data_path", DEFAULT_DATA_PATH, type=str)
        )
        btn_data = QPushButton("浏览...")
        btn_data.clicked.connect(self.browse_data)

        lbl_bat = QLabel("标定脚本(.bat)")
        self.edit_bat = QLineEdit(
            self.settings.value("bat_path", DEFAULT_BAT_PATH, type=str)
        )
        btn_bat = QPushButton("浏览...")
        btn_bat.clicked.connect(self.browse_bat)

        lbl_syn = QLabel("合成exe路径")
        self.edit_syn_exe = QLineEdit(
            self.settings.value("syn_exe", DEFAULT_SYN_EXE, type=str)
        )
        btn_syn = QPushButton("浏览...")
        btn_syn.clicked.connect(self.browse_syn_exe)

        lbl_ts = QLabel("全站仪数据路径")
        self.edit_ts_dir = QLineEdit(
            self.settings.value("ts_dir", DEFAULT_TS_DATA_DIR, type=str)
        )
        btn_ts = QPushButton("浏览...")
        btn_ts.clicked.connect(self.browse_ts_dir)

        files_layout.addWidget(lbl_data, 0, 0)
        files_layout.addWidget(self.edit_data, 1, 0, 1, 2)
        files_layout.addWidget(btn_data, 1, 2)
        files_layout.addWidget(lbl_bat, 2, 0)
        files_layout.addWidget(self.edit_bat, 3, 0, 1, 2)
        files_layout.addWidget(btn_bat, 3, 2)
        files_layout.addWidget(lbl_syn, 4, 0)
        files_layout.addWidget(self.edit_syn_exe, 5, 0, 1, 2)
        files_layout.addWidget(btn_syn, 5, 2)
        files_layout.addWidget(lbl_ts, 6, 0)
        files_layout.addWidget(self.edit_ts_dir, 7, 0, 1, 2)
        files_layout.addWidget(btn_ts, 7, 2)
        files_layout.setColumnStretch(0, 1)

        box_steps = QGroupBox("运行步骤")
        steps_layout = QVBoxLayout(box_steps)
        self.step_checks = {}
        for step in ALL_STEPS:
            cb = QCheckBox(step)
            cb.setChecked(True)
            self.step_checks[step] = cb
            steps_layout.addWidget(cb)
        steps_layout.addStretch(1)

        layout.addWidget(box_files)
        layout.addWidget(box_steps)
        layout.addWidget(self._build_result_panel())
        layout.addStretch(1)
        return panel

    def _build_result_panel(self):
        box = QGroupBox("测试结果")
        vbox = QVBoxLayout(box)

        grid = QGridLayout()
        self.result_labels = {}
        row = 0
        for name, _ in BUILDINGS:
            name_lbl = QLabel(name)
            name_lbl.setStyleSheet("font-size:14px;font-weight:bold;color:#333;")
            val_lbl = QLabel("--")
            val_lbl.setAlignment(Qt.AlignCenter)
            self.result_labels[name] = val_lbl
            grid.addWidget(name_lbl, row, 0)
            grid.addWidget(val_lbl, row, 1)
            row += 1

        # 分层结论行(全局, 不属于某栋)
        layer_name_lbl = QLabel("分层")
        layer_name_lbl.setStyleSheet("font-size:14px;font-weight:bold;color:#333;")
        self.layer_label = QLabel("--")
        self.layer_label.setAlignment(Qt.AlignCenter)
        grid.addWidget(layer_name_lbl, row, 0)
        grid.addWidget(self.layer_label, row, 1)

        grid.setColumnStretch(1, 1)
        vbox.addLayout(grid)

        # 分层备注
        note_lbl = QLabel("判断分层需要人工手动查看点云！！！")
        note_lbl.setWordWrap(True)
        note_lbl.setStyleSheet(
            "font-size:12px;font-weight:bold;color:#c62828;"
            "border:1px solid #c62828;border-radius:4px;padding:6px;"
        )
        vbox.addWidget(note_lbl)
        return box

    def _parse_precision_results(self, text):
        """解析精度输出文本, 返回 {楼栋显示名: 是否通过(True=通过/False=未通过)}"""
        results = {}
        current = None
        # 每个楼栋别名 -> 显示名
        alias_to_display = {}
        for display, aliases in BUILDINGS:
            results[display] = True
            for a in aliases:
                alias_to_display[a] = display

        over_count = {}     # 显示名 -> 平均误差与标准差均超限的位置数
        cur_display = None

        for raw in text.splitlines():
            line = raw.strip()
            if not line:
                continue
            # 位置数据行(含"位置精度"与"标准差")
            if "位置精度" in line and "平均距离" in line:
                import re as _re
                _num = r"[0-9.]+(?:[eE][+-]?[0-9]+)?"
                m_mean = _re.search(r"位置精度[^0-9]*(" + _num + r")", line)
                m_std = _re.search(r"标准差[^0-9]*(" + _num + r")", line)
                if m_mean and m_std and cur_display is not None:
                    try:
                        mean_val = float(m_mean.group(1))
                        std_val = float(m_std.group(1))
                    except ValueError:
                        continue
                    # 平均误差或标准差任一超限, 即该位置不通过
                    if mean_val > PRECISION_THRESHOLD or std_val > PRECISION_THRESHOLD:
                        over_count[cur_display] = over_count.get(cur_display, 0) + 1
                continue
            # 楼栋标题行: 判断属于哪个楼
            display = None
            for a, disp in alias_to_display.items():
                if a in line:
                    display = disp
                    break
            if display is not None:
                cur_display = display

        for disp, cnt in over_count.items():
            results[disp] = cnt < PRECISION_FAIL_COUNT
        return results

    def _parse_layer_result(self, text):
        """解析分层结论, 返回 (存在分层: bool, 层间距均值: float或None)"""
        import re as _re
        _num = r"[0-9.]+(?:[eE][+-]?[0-9]+)?"
        has_layer = False
        gap_values = []
        for raw in text.splitlines():
            line = raw.strip()
            if not line:
                continue
            if "结论" in line and "存在分层" in line:
                has_layer = True
            if "层间距" in line and "均值" in line:
                m = _re.search(r"均值\s*(" + _num + r")", line)
                if m:
                    try:
                        gap_values.append(float(m.group(1)))
                    except ValueError:
                        pass
            if "层间距离" in line and "均值" in line:
                m = _re.search(r"均值\s*(" + _num + r")", line)
                if m:
                    try:
                        gap_values.append(float(m.group(1)))
                    except ValueError:
                        pass
        # 存在分层时取较大的均值
        gap_mean = max(gap_values) if gap_values else None
        return has_layer, gap_mean

    def _update_results(self, text):
        results = self._parse_precision_results(text)
        for disp, passed in results.items():
            lbl = self.result_labels.get(disp)
            if lbl is None:
                continue
            if passed:
                lbl.setText("通过")
                lbl.setStyleSheet(
                    "font-size:16px;font-weight:bold;color:white;"
                    "background:#2e7d32;border-radius:6px;padding:4px;"
                )
            else:
                lbl.setText("未通过")
                lbl.setStyleSheet(
                    "font-size:16px;font-weight:bold;color:white;"
                    "background:#c62828;border-radius:6px;padding:4px;"
                )

        # 分层结论
        has_layer, gap_mean = self._parse_layer_result(text)
        # 有分层时在结论后显示层间距均值(单位m)
        gap_txt = ""
        if has_layer and gap_mean is not None:
            gap_txt = f" {gap_mean:.3f} m"
        if has_layer and gap_mean is not None and gap_mean > LAYER_GAP_THRESHOLD:
            self.layer_label.setText("未通过" + gap_txt)
            self.layer_label.setStyleSheet(
                "font-size:16px;font-weight:bold;color:white;"
                "background:#c62828;border-radius:6px;padding:4px;"
            )
        else:
            self.layer_label.setText("通过" + gap_txt)
            self.layer_label.setStyleSheet(
                "font-size:16px;font-weight:bold;color:white;"
                "background:#2e7d32;border-radius:6px;padding:4px;"
            )

    def browse_data(self):
        path = QFileDialog.getExistingDirectory(self, "选择数据文件夹")
        if path:
            self.edit_data.setText(path.replace("/", "\\") + "/")

    def browse_bat(self):
        path, _ = QFileDialog.getOpenFileName(
            self, "选择标定脚本", "", "批处理 (*.bat)"
        )
        if path:
            self.edit_bat.setText(path)

    def browse_syn_exe(self):
        path, _ = QFileDialog.getOpenFileName(
            self, "选择合成exe", "", "可执行程序 (*.exe)"
        )
        if path:
            self.edit_syn_exe.setText(path)

    def browse_ts_dir(self):
        path = QFileDialog.getExistingDirectory(self, "选择全站仪数据目录")
        if path:
            self.edit_ts_dir.setText(path.replace("/", "\\") + "/")

    def show_about(self):
        about = (
            "标定合成分析工具\n"
            "版本 " + REPORT_VERSION + "\n\n"
            "功能说明：\n"
            "· 数据合成：将雷达与全站仪采集数据合成为点云。\n"
            "· 标定并写入CFG：调用标定脚本并回写标定参数。\n"
            "· 精度计算：对比合成点云与全站仪打点，计算\n"
            "  平均误差与标准差，判定0号楼/一楼/二楼通过与否。\n"
            "· 误差棒图绘制：生成精度误差棒折线图。\n"
            "· 点云截取/分层分析：截取点云并检测点云分层，\n"
            "  分层需人工手动查看点云确认。\n\n"
            "使用方法：\n"
            "1. 配置数据文件夹、标定脚本、合成exe、全站仪数据路径。\n"
            "2. 勾选需要执行的运行步骤，点击【开始】。\n"
            "3. 结果在“精度输出”“测试结果”“图片展示”中查看。"
        )
        QMessageBox.information(self, "关于", about)

    def _save_paths(self):
        self.settings.setValue("data_path", self.edit_data.text().strip())
        self.settings.setValue("bat_path", self.edit_bat.text().strip())
        self.settings.setValue("syn_exe", self.edit_syn_exe.text().strip())
        self.settings.setValue("ts_dir", self.edit_ts_dir.text().strip())
        self.settings.sync()

    def start_run(self):
        if self.worker and self.worker.isRunning():
            return

        data_path = self.edit_data.text().strip()
        if not data_path:
            QMessageBox.warning(self, "提示", "请填写数据文件夹路径")
            return
        if not data_path.endswith(("/", "\\")):
            data_path += "/"
        if not Path(data_path).exists():
            QMessageBox.warning(self, "提示", f"数据文件夹不存在：\n{data_path}")
            return

        bat_path = self.edit_bat.text().strip()
        if self.step_checks[STEP_CALIBRATE].isChecked() and not Path(
            bat_path
        ).exists():
            QMessageBox.warning(self, "提示", f"标定脚本不存在：\n{bat_path}")
            return

        self._save_paths()

        enabled_steps = [
            step for step, cb in self.step_checks.items() if cb.isChecked()
        ]

        self.log_view.clear()
        self.precision_view.clear()
        self.precision_view.setExtraSelections([])
        self.image_list.clear()
        self._shown_images = set()
        self._user_stopped = False
        for lbl in self.result_labels.values():
            lbl.setText("--")
            lbl.setStyleSheet(
                "font-size:16px;font-weight:bold;color:#555;"
                "background:#e0e0e0;border-radius:6px;padding:4px;"
            )
        self.layer_label.setText("--")
        self.layer_label.setStyleSheet(
            "font-size:16px;font-weight:bold;color:#555;"
            "background:#e0e0e0;border-radius:6px;padding:4px;"
        )

        self.btn_start.setEnabled(False)
        self.btn_stop.setEnabled(True)
        self.lbl_status.setText("启动中...")

        syn_exe = self.edit_syn_exe.text().strip()
        ts_dir = self.edit_ts_dir.text().strip()

        cfg = {
            "data_path": data_path,
            "bat_path": bat_path,
            "syn_exe": syn_exe,
            "ts_dir": ts_dir,
            "steps": enabled_steps,
        }
        self.worker = ScriptProcess(cfg)
        self.worker.precision_ready.connect(self.on_precision)
        self.worker.images_ready.connect(self.show_images)
        self.worker.step_changed.connect(self.lbl_status.setText)
        self.worker.run_finished.connect(self.on_finished)
        self.log_timer.start()
        self.worker.start()

    def stop_run(self):
        if self.worker and self.worker.isRunning():
            self._user_stopped = True
            self.btn_stop.setEnabled(False)
            self.lbl_status.setText("正在停止...")
            self.worker.request_stop()

    def flush_log(self):
        if not self.worker:
            return
        chunk = self.worker.drain_text()
        if chunk:
            self.log_view.moveCursor(self.log_view.textCursor().End)
            self.log_view.insertPlainText(chunk)
            self.log_view.moveCursor(self.log_view.textCursor().End)

    def on_precision(self, text):
        self._apply_precision_text(text)
        self._update_results(text)

    def _apply_precision_text(self, text):
        """设置精度输出文本, 并将平均误差或标准差任一超过阈值的位置行整行标红"""
        self.precision_view.setPlainText(text)
        selections = []
        for i, raw in enumerate(text.splitlines()):
            line = raw.strip()
            if "位置精度" in line and "平均距离" in line:
                import re as _re
                _num = r"[0-9.]+(?:[eE][+-]?[0-9]+)?"
                m_mean = _re.search(r"位置精度[^0-9]*(" + _num + r")", line)
                m_std = _re.search(r"标准差[^0-9]*(" + _num + r")", line)
                if m_mean and m_std:
                    try:
                        mean_val = float(m_mean.group(1))
                        std_val = float(m_std.group(1))
                    except ValueError:
                        continue
                    if mean_val > PRECISION_THRESHOLD or std_val > PRECISION_THRESHOLD:
                        sel = QTextEdit.ExtraSelection()
                        sel.format.setBackground(QColor("#f8c8c8"))
                        sel.format.setProperty(QTextFormat.FullWidthSelection, True)
                        # 定位到该行
                        block = self.precision_view.document().findBlockByNumber(i)
                        cursor = QTextCursor(block)
                        cursor.select(QTextCursor.LineUnderCursor)
                        sel.cursor = cursor
                        selections.append(sel)
        self.precision_view.setExtraSelections(selections)

    def show_images(self, paths):
        if not hasattr(self, "_shown_images"):
            self._shown_images = set()
        for p in paths:
            if not Path(p).exists():
                continue
            # 同一张图只显示一次
            try:
                key = str(Path(p).resolve())
            except OSError:
                key = str(p)
            if key in self._shown_images:
                continue
            self._shown_images.add(key)
            item = QListWidgetItem(QIcon(p), Path(p).name)
            item.setData(Qt.UserRole, p)
            item.setToolTip(p)
            self.image_list.addItem(item)
        if self.image_list.count() > 0:
            self.image_list.setCurrentRow(self.image_list.count() - 1)

    def open_image_viewer(self, item):
        path = item.data(Qt.UserRole)
        if path:
            ImageViewer(path, self).exec_()

    def on_finished(self, ok):
        self.flush_log()
        self.log_timer.stop()
        self.btn_start.setEnabled(True)
        self.btn_stop.setEnabled(False)
        if ok:
            self.lbl_status.setText("完成")
        elif self._user_stopped:
            self.lbl_status.setText("已停止")
        else:
            self.lbl_status.setText("出错退出")
            QMessageBox.warning(
                self, "运行结束", "脚本异常退出，请查看【运行内容】中的报错信息。"
            )

    def closeEvent(self, event):
        if self.worker and self.worker.isRunning():
            self.worker.request_stop()
            self.worker.wait(5000)
        super().closeEvent(event)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    win = MainWindow()
    win.show()
    sys.exit(app.exec_())
