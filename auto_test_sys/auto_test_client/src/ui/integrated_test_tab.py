from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGridLayout, QScrollArea,
    QPushButton, QLabel, QTextEdit, QProgressBar, QGroupBox,
    QFileDialog, QMessageBox, QLineEdit, QSpinBox, QDoubleSpinBox, QComboBox
)
from PyQt5.QtCore import Qt, QThread, pyqtSignal, QTimer
import json
import os
from datetime import datetime

from src.ui.components import (
    ModuleGroupBox, ControlButton, StatusLabel, ResultDisplay,
    TestProgressWidget, ModuleSelector
)
from src.utils.logger import get_logger
from src.api.client import TestReportGenerator


class IntegratedTestThread(QThread):
    """集成测试线程"""
    progress_updated = pyqtSignal(int, int, str)  # (current, total, status)
    test_completed = pyqtSignal(dict, str, str)   # (result, module, test_name)
    finished_signal = pyqtSignal(dict)            # (final_report)
    wait_notification = pyqtSignal(str, int)      # (message, seconds) 等待通知信号
    
    def __init__(self, api_client, selected_modules, config_manager):
        super().__init__()
        self.api_client = api_client
        self.selected_modules = selected_modules
        self.config_manager = config_manager
        self.report_generator = TestReportGenerator()
        self.is_running = False
    
    def run(self):
        """执行集成测试"""
        self.is_running = True
        test_cases = self.prepare_test_cases()
        total_tests = len(test_cases)
        
        self.progress_updated.emit(0, total_tests, "开始执行集成测试...")
        
        for i, test_case in enumerate(test_cases):
            if not self.is_running:
                break
                
            # 解析测试用例参数
            if len(test_case) == 4:
                module, test_name, test_func, args = test_case
                wait_time = 0  # 默认无等待
            elif len(test_case) == 5:
                module, test_name, test_func, args, wait_time = test_case
            else:
                continue
                
            self.progress_updated.emit(i, total_tests, f"执行测试: {test_name}")
            
            try:
                # 执行测试
                result = test_func(*args) if args else test_func()
                
                # 添加到报告
                self.report_generator.add_result(module, test_name, result)
                
                # 发送测试完成信号
                self.test_completed.emit(result, module, test_name)
                
                # 如果有等待时间，执行等待
                if wait_time > 0:
                    self.execute_wait(test_name, wait_time)
                
            except Exception as e:
                error_result = {
                    "success": False,
                    "message": f"测试执行异常: {str(e)}",
                    "error": str(e)
                }
                self.report_generator.add_result(module, test_name, error_result)
                self.test_completed.emit(error_result, module, test_name)
            
            # 短暂延迟避免过于频繁的请求
            self.msleep(100)
        
        # 发送最终报告
        final_report = self.report_generator.generate_report()
        self.finished_signal.emit(final_report)
        self.progress_updated.emit(total_tests, total_tests, "测试完成")
        self.is_running = False
    
    def prepare_test_cases(self):
        """准备测试用例"""
        test_cases = []

        # 系统信息测试
        if "system" in self.selected_modules:
            test_cases.extend([
                ("系统信息", "获取系统信息", self.api_client.get_system_info, [], 0),
                ("系统信息", "获取系统指标", self.api_client.get_system_metrics, [], 0),
                ("系统信息", "获取电池状态", self.api_client.get_battery_status, [], 0),
                ("系统信息", "获取TF卡状态", self.api_client.get_tf_card_status, [], 0),
                # 补充缺失的全部模块状态查询测试
                # ("系统信息", "查询全部模块电源状态", self.api_client.get_devices_status, [], 0)
            ])

        # 电源管理测试
        if "power" in self.selected_modules:
            power_modules = self.config_manager.get("modules.power.modules", [])
            for module in power_modules:
                test_cases.extend([
                    ("电源管理", f"{module}上电测试", self.api_client.power_on, [module], 0),
                    ("电源管理", f"{module}断电测试", self.api_client.power_off, [module], 0),
                    ("电源管理", f"{module}状态查询", self.api_client.get_power_status, [module], 0)
                ])
            test_cases.extend([
                ("电源管理", "全部断电测试", self.api_client.power_off_all, [], 0),
                ("电源管理", "全部上电测试", self.api_client.power_on_all, [], 30)  # 全部上电后等待30秒
            ])

        # 配置管理测试
        if "config" in self.selected_modules:
            test_cases.extend([
                ("配置管理", "配置Wi-Fi", self.api_client.wifi_setup, [], 0),
                # ("配置管理", "配置转台", self.api_client.motor_configure, [], 0),
                # ("配置管理", "配置小电机", self.api_client.min_motor_configure, [], 0),
                # ("配置管理", "配置雷达", self.api_client.lidar_setup, [], 0),
                ("配置管理", "一键配置所有硬件", self.api_client.setup_all_devices, [], 0)
            ])

        # 转台控制测试
        if "turret" in self.selected_modules:
            test_cases.extend([
                ("转台控制", "转台找零位", self.api_client.motor_find_zero, [30], 0),
                ("转台控制", "转台设置位置90", self.api_client.motor_set_position, [90.0, 30], 0),
                ("转台控制", "转台设置速度2.94", self.api_client.motor_set_speed, [5.0], 10),
                ("转台控制", "转台设置速度20", self.api_client.motor_set_speed, [20.0], 10),
                ("转台控制", "转台设置速度-20", self.api_client.motor_set_speed, [-20.0], 10),
                ("转台控制", "转台回0", self.api_client.motor_set_position, [0,30], 0),
            ])
        
        # 小电机控制测试
        if "mini_motor" in self.selected_modules:
            test_cases.extend([
                ("小电机控制", "获取小电机限位角度", self.api_client.min_motor_detect_limits, [300, 100], 0),
                ("小电机控制", "小电机相对移动15", self.api_client.min_motor_relative_move, [15.0, 20], 3),
                ("小电机控制", "小电机相对移动15", self.api_client.min_motor_relative_move, [15.0, 20], 3),
                ("小电机控制", "小电机相对移动-15", self.api_client.min_motor_relative_move, [-15.0, 20], 3),
                ("小电机控制", "小电机相对移动-15", self.api_client.min_motor_relative_move, [-15.0, 20], 3),
                ("小电机控制", "读取小电机角度", self.api_client.min_motor_read_angle, [], 0),
            ])
        
        # 相机控制测试
        if "camera" in self.selected_modules:
            test_cases.extend([
                ("相机控制", "获取分辨率列表", self.api_client.get_camera_resolutions, [], 0),
                ("相机控制", "设置相机0分辨率", self.api_client.camera_set_resolution, ["/dev/video0", "1080p"], 0),
                ("相机控制", "设置相机1分辨率", self.api_client.camera_set_resolution, ["/dev/video2", "1080p"], 0),
                ("相机控制", "相机0拍照", self.api_client.camera_capture, ["/dev/video0", "test1.jpg"], 0),
                ("相机控制", "相机1拍照", self.api_client.camera_capture, ["/dev/video2", "test2.jpg"], 0),
            ])
        
        # LED控制测试
        if "led" in self.selected_modules:
            test_cases.extend([
                ("LED控制", "设置红色", self.api_client.led_set_custom_color, [255, 0, 0], 10),
                ("LED控制", "设置绿色", self.api_client.led_set_custom_color, [0, 255, 0], 10),
                ("LED控制", "设置蓝色", self.api_client.led_set_custom_color, [0, 0, 255], 0),
            ])
        
        # 雷达控制测试
        if "lidar" in self.selected_modules:
            test_cases.extend([
                ("雷达控制", "获取雷达序列号", self.api_client.lidar_get_sn, [], 0),
                ("雷达控制", "获取雷达校准参数", self.api_client.lidar_get_calibration, [], 0)
            ])
        
        # 倾角仪控制测试
        if "inclinometer" in self.selected_modules:
            test_cases.extend([
                ("倾角仪控制", "读取倾角仪数据", self.api_client.inclinometer_read, [], 0)
            ])
        

        
        return test_cases
    
    def stop_test(self):
        """停止测试"""
        self.is_running = False
    
    def execute_wait(self, test_name, wait_time):
        """执行等待函数，支持界面倒计时显示"""
        if wait_time <= 0:
            return
            
        # 发送等待开始通知
        self.wait_notification.emit(f"{test_name}执行完成，等待{wait_time}秒...", wait_time)
        
        # 执行倒计时等待
        for second in range(wait_time, 0, -1):
            if not self.is_running:
                break
            self.wait_notification.emit(f"{test_name}等待中... 剩余 {second} 秒", second)
            self.sleep(1)  # 每秒更新一次
        
        if self.is_running:
            self.wait_notification.emit(f"{test_name}等待完成，继续执行后续测试", 0)


class IntegratedTestTab(QWidget):
    """集成模块化测试标签页"""
    
    def __init__(self, api_client, config_manager, parent=None):
        super().__init__(parent)
        self.api_client = api_client
        self.config_manager = config_manager
        self.logger = get_logger(config_manager)
        self.test_thread = None
        
        self.init_ui()
    
    def init_ui(self):
        """初始化UI"""
        main_layout = QHBoxLayout(self)
        
        # 左侧面板 - 测试配置
        self.create_config_panel(main_layout)
        
        # 右侧面板 - 测试执行和结果显示
        self.create_test_panel(main_layout)
    
    def create_config_panel(self, parent):
        """创建配置面板"""
        config_widget = QWidget()
        config_widget.setMaximumWidth(300)
        config_layout = QVBoxLayout(config_widget)
        
        # 测试配置组
        config_group = ModuleGroupBox("测试配置")
        config_layout.addWidget(config_group)
        
        config_inner_layout = QVBoxLayout()
        config_group.setLayout(config_inner_layout)
        
        # 模块选择器
        self.module_selector = ModuleSelector(self.config_manager.get_enabled_modules())
        self.module_selector.selection_changed.connect(self.on_module_selection_changed)
        config_inner_layout.addWidget(self.module_selector)
        
        # 测试选项
        options_group = ModuleGroupBox("测试选项")
        config_inner_layout.addWidget(options_group)
        
        options_layout = QVBoxLayout()
        options_group.setLayout(options_layout)
        
        # 测试参数设置
        self.delay_input = ParameterInput("测试间隔(ms)", "number")
        self.delay_input.set_value(500)
        options_layout.addWidget(self.delay_input)
        
        self.retry_input = ParameterInput("失败重试次数", "number")
        self.retry_input.set_value(3)
        options_layout.addWidget(self.retry_input)
        
        # 测试控制按钮
        control_group = ModuleGroupBox("测试控制")
        config_inner_layout.addWidget(control_group)
        
        control_layout = QVBoxLayout()
        control_group.setLayout(control_layout)
        
        self.start_test_btn = ControlButton("开始测试")
        self.start_test_btn.clicked.connect(self.start_integrated_test)
        control_layout.addWidget(self.start_test_btn)
        
        self.stop_test_btn = ControlButton("停止测试")
        self.stop_test_btn.clicked.connect(self.stop_integrated_test)
        self.stop_test_btn.setEnabled(False)
        control_layout.addWidget(self.stop_test_btn)
        
        self.generate_report_btn = ControlButton("生成报告")
        self.generate_report_btn.clicked.connect(self.generate_test_report)
        self.generate_report_btn.setEnabled(False)
        control_layout.addWidget(self.generate_report_btn)
        
        # 报告导出
        export_group = ModuleGroupBox("报告导出")
        config_inner_layout.addWidget(export_group)
        
        export_layout = QVBoxLayout()
        export_group.setLayout(export_layout)
        
        self.export_json_btn = ControlButton("导出JSON报告")
        self.export_json_btn.clicked.connect(lambda: self.export_report("json"))
        export_layout.addWidget(self.export_json_btn)
        
        self.export_txt_btn = ControlButton("导出TXT报告")
        self.export_txt_btn.clicked.connect(lambda: self.export_report("txt"))
        export_layout.addWidget(self.export_txt_btn)
        
        config_inner_layout.addStretch()
        parent.addWidget(config_widget)
    
    def create_test_panel(self, parent):
        """创建测试面板"""
        test_widget = QWidget()
        test_layout = QVBoxLayout(test_widget)
        
        # 测试进度
        self.test_progress = TestProgressWidget()
        test_layout.addWidget(self.test_progress)
        
        # 测试状态
        status_group = ModuleGroupBox("测试状态")
        test_layout.addWidget(status_group)
        
        status_layout = QVBoxLayout()
        status_group.setLayout(status_layout)
        
        self.current_test_label = StatusLabel("当前测试: 无")
        status_layout.addWidget(self.current_test_label)
        
        self.test_result_label = StatusLabel("测试结果: 等待开始")
        status_layout.addWidget(self.test_result_label)
        
        # 详细结果显示
        result_group = ModuleGroupBox("测试详情")
        test_layout.addWidget(result_group)
        
        result_layout = QVBoxLayout()
        result_group.setLayout(result_layout)
        
        self.test_result_display = ResultDisplay()
        result_layout.addWidget(self.test_result_display)
        
        # 最终报告显示
        report_group = ModuleGroupBox("测试报告")
        test_layout.addWidget(report_group)
        
        report_layout = QVBoxLayout()
        report_group.setLayout(report_layout)
        
        self.final_report_display = QTextEdit()
        self.final_report_display.setReadOnly(True)
        self.final_report_display.setMaximumHeight(200)
        report_layout.addWidget(self.final_report_display)
        
        parent.addWidget(test_widget)
    
    def on_module_selection_changed(self, selected_modules):
        """模块选择改变时的处理"""
        self.logger.info(f"选中的测试模块: {selected_modules}")
        # 可以在这里更新测试用例预览等
    
    def start_integrated_test(self):
        """开始集成测试"""
        selected_modules = self.module_selector.get_selected_modules()
        
        if not selected_modules:
            QMessageBox.warning(self, "警告", "请至少选择一个测试模块")
            return
        
        self.logger.info(f"开始集成测试，选中模块: {selected_modules}")
        
        # 更新UI状态
        self.start_test_btn.setEnabled(False)
        self.stop_test_btn.setEnabled(True)
        self.generate_report_btn.setEnabled(False)
        self.export_json_btn.setEnabled(False)
        self.export_txt_btn.setEnabled(False)
        self.test_result_display.clear()
        self.final_report_display.clear()
        
        # 禁用其他可能干扰的按钮
        self._disable_control_buttons()
        
        # 创建并启动测试线程
        self.test_thread = IntegratedTestThread(
            self.api_client, 
            selected_modules, 
            self.config_manager
        )
        
        # 连接信号
        self.test_thread.progress_updated.connect(self.update_test_progress)
        self.test_thread.test_completed.connect(self.handle_test_result)
        self.test_thread.finished_signal.connect(self.handle_test_finished)
        self.test_thread.wait_notification.connect(self.handle_wait_notification)
        self.test_thread.finished.connect(self._on_test_thread_finished)
        
        # 启动测试
        self.test_thread.start()
    
    def stop_integrated_test(self):
        """停止集成测试"""
        if self.test_thread and self.test_thread.isRunning():
            self.logger.info("停止集成测试")
            self.test_thread.stop_test()
            self.test_thread.wait()
        
        # 更新UI状态
        self._enable_control_buttons()
        self.test_progress.set_status("测试已停止", False)
    
    def update_test_progress(self, current, total, status):
        """更新测试进度"""
        self.test_progress.set_progress(current, total)
        self.test_progress.set_status(status)
        #self.current_test_label.set_status(status)
        if status.startswith("执行测试:"):
            test_name = status.replace("执行测试:", "").strip()
            self.current_test_label.set_status(f"当前测试：{test_name}")
    
    def handle_test_result(self, result, module, test_name):
        """处理单个测试结果"""
        success = result.get("success", False)
        message = result.get("message", "未知结果")
        
        # 显示测试结果
        self.test_result_display.append_result(
            f"[{module}] {test_name}: {message}", 
            success
        )
        
        # 更新状态标签
        status_text = "通过" if success else "失败"
        self.test_result_label.set_status(f"{test_name}: {status_text}", success)
        
        # 记录日志
        self.logger.info(f"测试完成 - {module}.{test_name}: {'成功' if success else '失败'}")
    
    def handle_test_finished(self, report):
        """处理测试完成"""
        self.logger.info("集成测试完成")
        
        # 更新UI状态
        self._enable_control_buttons()
        self.generate_report_btn.setEnabled(True)
        
        # 显示最终报告
        self.display_final_report(report)
        
        # 保存报告数据
        self.final_report = report
    
    def handle_wait_notification(self, message, seconds):
        """处理等待通知"""
        # 更新状态显示
        self.test_progress.set_status(message)
        #self.current_test_label.set_status(message)
        
        # 如果有倒计时，更新进度条
        if seconds > 0:
            # 计算进度百分比 (30秒倒计时)
            progress_percent = int((30 - seconds) / 30 * 100)
            self.test_progress.set_progress(progress_percent, 100)
        
        # 记录日志
        self.logger.info(f"等待通知: {message}")
    
    def display_final_report(self, report):
        """显示最终报告"""
        summary = report.get("summary", {})
        details = report.get("details", [])
        
        report_text = f"""=== 集成测试报告 ===
生成时间: {report.get('generated_at', '未知')}
        
测试摘要:
- 总测试数: {summary.get('total_tests', 0)}
- 通过测试: {summary.get('passed_tests', 0)}
- 失败测试: {summary.get('failed_tests', 0)}
- 通过率: {summary.get('pass_rate', '0%')}

详细结果:"""
        
        for detail in details:
            module = detail.get('module', 'Unknown')
            test_name = detail.get('test_name', 'Unknown')
            result = detail.get('result', {})
            success = "✓" if result.get('success', False) else "✗"
            message = result.get('message', 'Unknown')
            
            report_text += f"\n{success} [{module}] {test_name}: {message}"
        
        self.final_report_display.setPlainText(report_text)
        self.test_progress.set_status("测试完成", True)
    
    def generate_test_report(self):
        """生成测试报告"""
        if hasattr(self, 'final_report'):
            self.display_final_report(self.final_report)
            QMessageBox.information(self, "成功", "测试报告已生成并显示")
        else:
            QMessageBox.warning(self, "警告", "暂无测试报告可生成")
    
    def export_report(self, format_type):
        """导出报告"""
        if not hasattr(self, 'final_report'):
            QMessageBox.warning(self, "警告", "请先完成测试生成报告")
            return
        
        # 临时禁用导出按钮防止重复点击
        export_btn = self.export_json_btn if format_type == "json" else self.export_txt_btn
        export_btn.setEnabled(False)
        
        # 选择保存文件
        file_filter = "JSON Files (*.json)" if format_type == "json" else "Text Files (*.txt)"
        file_path, _ = QFileDialog.getSaveFileName(
            self, 
            f"导出{format_type.upper()}报告",
            f"test_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.{format_type}",
            file_filter
        )
        
        # 恢复按钮状态
        export_btn.setEnabled(True)
        
        if not file_path:
            return
        
        try:
            if format_type == "json":
                with open(file_path, 'w', encoding='utf-8') as f:
                    json.dump(self.final_report, f, ensure_ascii=False, indent=2)
            else:
                # 生成文本格式报告
                report_text = self.format_report_as_text(self.final_report)
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(report_text)
            
            QMessageBox.information(self, "成功", f"报告已导出到: {file_path}")
            self.logger.info(f"报告已导出: {file_path}")
            
        except Exception as e:
            QMessageBox.critical(self, "错误", f"导出报告失败: {str(e)}")
            self.logger.error(f"导出报告失败: {str(e)}")
    
    def format_report_as_text(self, report):
        """将报告格式化为文本"""
        summary = report.get("summary", {})
        details = report.get("details", [])
        
        lines = [
            "=" * 50,
            "自动化测试报告",
            "=" * 50,
            f"生成时间: {report.get('generated_at', '未知')}",
            "",
            "测试摘要:",
            f"  总测试数: {summary.get('total_tests', 0)}",
            f"  通过测试: {summary.get('passed_tests', 0)}",
            f"  失败测试: {summary.get('failed_tests', 0)}",
            f"  通过率: {summary.get('pass_rate', '0%')}",
            "",
            "详细测试结果:",
            "-" * 30
        ]
        
        for detail in details:
            module = detail.get('module', 'Unknown')
            test_name = detail.get('test_name', 'Unknown')
            result = detail.get('result', {})
            success = "通过" if result.get('success', False) else "失败"
            message = result.get('message', 'Unknown')
            
            lines.append(f"[{module}] {test_name}")
            lines.append(f"  结果: {success}")
            lines.append(f"  信息: {message}")
            lines.append("")
        
        return "\n".join(lines)
    
    def refresh(self):
        """刷新页面"""
        self.logger.info("刷新集成测试页面")
        # 重置显示内容
        self.test_result_display.clear()
        self.final_report_display.clear()
        self.test_progress.set_progress(0, 100)
        self.test_progress.set_status("就绪")
        self.current_test_label.set_status("当前测试: 无")
        self.test_result_label.set_status("测试结果: 等待开始")
        
        # 如果测试正在进行，保持按钮状态；否则恢复默认状态
        if not (self.test_thread and self.test_thread.isRunning()):
            self._enable_control_buttons()
    
    def _disable_control_buttons(self):
        """禁用控制按钮"""
        # 禁用可能导致冲突的操作按钮
        if hasattr(self.parent(), 'individual_control_tab'):
            # 如果能找到单模块控制标签页，可以考虑禁用其中的相关按钮
            # 这里暂时不实现跨标签页的按钮禁用
            pass
        
        self.logger.debug("禁用集成测试控制按钮")
    
    def _enable_control_buttons(self):
        """启用控制按钮"""
        self.start_test_btn.setEnabled(True)
        self.stop_test_btn.setEnabled(False)
        self.export_json_btn.setEnabled(True)
        self.export_txt_btn.setEnabled(True)
        self.logger.debug("启用集成测试控制按钮")
    
    def _on_test_thread_finished(self):
        """测试线程完成时的回调"""
        self.logger.debug("集成测试线程完成")


class ParameterInput(QWidget):
    """参数输入组件（简化版，用于集成测试配置）"""
    
    def __init__(self, param_name: str, param_type: str = "text", parent=None):
        super().__init__(parent)
        self.param_name = param_name
        self.param_type = param_type
        self.setup_ui()
    
    def setup_ui(self):
        layout = QHBoxLayout(self)
        
        # 参数标签
        label = QLabel(f"{self.param_name}:")
        label.setMinimumWidth(120)
        layout.addWidget(label)
        
        # 根据参数类型创建输入控件
        if self.param_type == "text":
            self.input_widget = QLineEdit()
        elif self.param_type == "number":
            self.input_widget = QSpinBox()
            self.input_widget.setRange(0, 999999)
        else:
            self.input_widget = QLineEdit()
        
        layout.addWidget(self.input_widget)
    
    def get_value(self):
        """获取输入值"""
        if isinstance(self.input_widget, QLineEdit):
            return self.input_widget.text()
        elif isinstance(self.input_widget, QSpinBox):
            return self.input_widget.value()
        else:
            return self.input_widget.text()
    
    def set_value(self, value):
        """设置输入值"""
        if isinstance(self.input_widget, QLineEdit):
            self.input_widget.setText(str(value))
        elif isinstance(self.input_widget, QSpinBox):
            self.input_widget.setValue(int(value))