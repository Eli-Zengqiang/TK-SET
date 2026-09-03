"""自动化测试标签页"""

from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGridLayout, QSplitter,
    QPushButton, QLabel, QTextEdit, QComboBox, QListWidget,
    QListWidgetItem, QTableWidget, QTableWidgetItem, QHeaderView,
    QGroupBox, QProgressBar, QFileDialog, QMessageBox, QSpinBox,
    QDoubleSpinBox, QLineEdit, QCheckBox, QTabWidget
)
from PyQt5.QtCore import Qt, QThread, pyqtSignal, QTimer
from PyQt5.QtGui import QFont, QColor, QBrush
import json
import os
from datetime import datetime
from typing import List, Dict, Any

from src.ui.components import (
    ModuleGroupBox, ControlButton, StatusLabel, ResultDisplay
)
from src.utils.logger import get_logger
from src.auto_test.base import TestSuite, TestResult, TestStatus, TestCaseConfig
from src.auto_test.template_manager import TemplateManager



class AutoTestWorker(QThread):
    """自动化测试工作线程"""
    
    # 信号定义
    test_started = pyqtSignal(str)  # 测试开始信号 (测试名称)
    test_completed = pyqtSignal(TestResult)  # 测试完成信号
    suite_completed = pyqtSignal(dict)  # 套件完成信号 (汇总信息)
    progress_updated = pyqtSignal(int, int)  # 进度更新信号 (当前, 总数)
    process_log_updated = pyqtSignal(str, str)  # 进程日志更新信号 (level, message)
    step_progress_updated = pyqtSignal(str, int, int)  # 步骤进度更新信号 (description, current, total)
    test_stopped = pyqtSignal()  # 【新增】测试被用户停止的信号

    def __init__(self, test_suite: TestSuite):
        super().__init__()
        self.test_suite = test_suite
        self._is_running = False
    
    def run(self):
        """运行测试套件"""
        self._is_running = True
        
        # 连接测试用例的进程日志信号
        for test_case in self.test_suite.test_cases:
            test_case.process_log.connect(self._handle_process_log)
            test_case.step_progress.connect(self._handle_step_progress)
        
        # 修改TestSuite的run_all方法以支持停止功能
        results = self._run_test_suite_with_stop_support()

        # 发送套件完成信号 (仅当正常完成时)
        if self._is_running:  # 只有未被停止时才发送完成信号
            summary = self.test_suite.get_summary()
            self.suite_completed.emit(summary)
        else:
            # 如果被停止，发送一个“被停止”的汇总信息
            stopped_summary = {
                "suite_name": self.test_suite.name,
                "total_tests": len(self.test_suite.test_cases),
                "passed_tests": len([r for r in self.test_suite.results if r.status == TestStatus.PASSED]),
                "failed_tests": len([r for r in self.test_suite.results if r.status == TestStatus.FAILED]),
                "error_tests": len([r for r in self.test_suite.results if r.status == TestStatus.ERROR]),
                "skipped_tests": len([r for r in self.test_suite.results if r.status == TestStatus.SKIPPED]),
                "pass_rate": "0%",
                "results": [r.to_dict() for r in self.test_suite.results] if hasattr(self.test_suite, 'results') else []
            }
            self.suite_completed.emit(stopped_summary)
            self.test_stopped.emit()  # 【新增】发出停止信号
        self._is_running = False
    
    def _run_test_suite_with_stop_support(self):
        """带停止支持的测试套件运行"""
        self.test_suite.results.clear()
        
        self.test_suite.logger.info(f"开始运行测试套件: {self.test_suite.name}")
        self.test_suite.logger.info(f"共 {len(self.test_suite.test_cases)} 个测试用例")

        total_tests = len(self.test_suite.test_cases)

        for i, test_case in enumerate(self.test_suite.test_cases, 1):
            # 检查是否应该停止
            if not self._is_running:
                self.test_suite.logger.info("测试被用户停止")
                # 将剩余测试标记为跳过
                for remaining_test in self.test_suite.test_cases[i-1:]:
                    if remaining_test.result is None:
                        remaining_test.result = TestResult(
                            test_name=remaining_test.config.name,
                            status=TestStatus.SKIPPED,
                            message="测试被用户停止"
                        )
                        self.test_suite.results.append(remaining_test.result)
                break
            self.progress_updated.emit(i, total_tests)
            self.test_started.emit(test_case.config.name)
            self.test_suite.logger.info(f"运行测试用例 ({i}/{len(self.test_suite.test_cases)}): {test_case.config.name}")
            
            try:
                result = test_case.run()
                self.test_suite.results.append(result)
                self.test_completed.emit(result)
                # 记录结果
                if result.status == TestStatus.PASSED:
                    self.test_suite.logger.info(f"\u2713 测试通过: {test_case.config.name}")
                elif result.status == TestStatus.FAILED:
                    self.test_suite.logger.warning(f"\u2717 测试失败: {test_case.config.name} - {result.message}")
                elif result.status == TestStatus.SKIPPED:
                    self.test_suite.logger.info(f"\u25e6 测试跳过: {test_case.config.name} - {result.message}")
                else:
                    self.test_suite.logger.error(f"\u26a0 测试异常: {test_case.config.name} - {result.message}")
                    
            except Exception as e:
                error_result = TestResult(
                    test_name=test_case.config.name,
                    status=TestStatus.ERROR,
                    message=f"测试套件执行异常：{str(e)}",
                    error_info=str(e)
                )
                self.test_suite.results.append(error_result)
                self.test_suite.logger.error(f"测试套件执行异常：{test_case.config.name} - {str(e)}")
                # 【关键修复】异常情况下也需要发射测试完成信号
                self.test_completed.emit(error_result)
            # 再次检查停止标志（单个测试用例完成后）
            if not self._is_running:
                self.test_suite.logger.info("测试被用户停止")
                # 将剩余测试标记为跳过
                for remaining_test in self.test_suite.test_cases[i:]:
                    if remaining_test.result is None:
                        remaining_test.result = TestResult(
                            test_name=remaining_test.config.name,
                            status=TestStatus.SKIPPED,
                            message="测试被用户停止"
                        )
                        self.test_suite.results.append(remaining_test.result)
                        self.test_completed.emit(remaining_test.result)
                break
        if self._is_running:
            self.progress_updated.emit(total_tests, total_tests)
        self.test_suite.logger.info(f"测试套件执行完成: {self.test_suite.name}")
        return self.test_suite.results
    
    def _handle_process_log(self, level: str, message: str):
        """处理进程日志信号"""
        self.process_log_updated.emit(level, message)
    
    def _handle_step_progress(self, description: str, current: int, total: int):
        """处理步骤进度信号"""
        self.step_progress_updated.emit(description, current, total)
    
    def stop(self):
        """停止测试"""
        if not self._is_running:
            return

        self._is_running = False
        # 通知所有测试用例停止
        for test_case in self.test_suite.test_cases:
            if hasattr(test_case, 'stop_test'):
                test_case.stop_test()


class AutoTestTab(QWidget):
    """自动化测试标签页"""
    
    def __init__(self, api_client, config_manager, parent=None):
        super().__init__(parent)
        self.api_client = api_client
        self.config_manager = config_manager
        self.logger = get_logger(config_manager)
        self.template_manager = TemplateManager()
        self.current_test_suite = None
        self.test_worker = None
        self._was_stopped_by_user = False
        self._test_row_map = {}  # 【新增】测试名称到表格行号的映射

        self.init_ui()
        self.load_templates()
    
    def init_ui(self):
        """初始化UI"""
        main_layout = QHBoxLayout(self)
        
        # 创建分割器
        splitter = QSplitter(Qt.Horizontal)
        main_layout.addWidget(splitter)
        
        # 左侧面板 - 模板和配置
        self.create_left_panel(splitter)
        
        # 右侧面板 - 测试执行和结果显示
        self.create_right_panel(splitter)
        
        # 设置分割比例
        splitter.setSizes([300, 900])
    
    def create_left_panel(self, parent):
        """创建左侧面板"""
        left_widget = QWidget()
        left_layout = QVBoxLayout(left_widget)
        
        # 模板选择组
        template_group = ModuleGroupBox("测试模板")
        left_layout.addWidget(template_group)
        
        template_layout = QVBoxLayout()
        template_group.setLayout(template_layout)
        
        # 模板下拉选择
        self.template_combo = QComboBox()
        self.template_combo.currentTextChanged.connect(self.on_template_selected)
        template_layout.addWidget(self.template_combo)
        
        # 模板操作按钮
        template_btn_layout = QHBoxLayout()
        self.load_template_btn = ControlButton("加载模板")
        self.load_template_btn.clicked.connect(self.load_selected_template)
        template_btn_layout.addWidget(self.load_template_btn)
        
        self.refresh_templates_btn = ControlButton("刷新模板")
        self.refresh_templates_btn.clicked.connect(self.load_templates)
        template_btn_layout.addWidget(self.refresh_templates_btn)
        
        template_layout.addLayout(template_btn_layout)
        
        # 测试用例列表
        case_group = ModuleGroupBox("测试用例")
        left_layout.addWidget(case_group)
        
        case_layout = QVBoxLayout()
        case_group.setLayout(case_layout)
        
        self.test_case_list = QListWidget()
        self.test_case_list.itemChanged.connect(self.on_test_case_selection_changed)
        case_layout.addWidget(self.test_case_list)
        
        # 全选/反选按钮
        select_layout = QHBoxLayout()
        self.select_all_btn = ControlButton("全选")
        self.select_all_btn.clicked.connect(self.select_all_cases)
        select_layout.addWidget(self.select_all_btn)
        
        self.deselect_all_btn = ControlButton("清空")
        self.deselect_all_btn.clicked.connect(self.deselect_all_cases)
        select_layout.addWidget(self.deselect_all_btn)
        
        case_layout.addLayout(select_layout)
        
        # 测试配置组
        # config_group = ModuleGroupBox("测试配置")
        # left_layout.addWidget(config_group)
        #
        # config_layout = QGridLayout()
        # config_group.setLayout(config_layout)
        #
        # # 并发数设置
        # self.concurrent_spin = QSpinBox()
        # self.concurrent_spin.setRange(1, 10)
        # self.concurrent_spin.setValue(1)
        # config_layout.addWidget(QLabel("并发数:"), 0, 0)
        # config_layout.addWidget(self.concurrent_spin, 0, 1)
        #
        # # 失败停止选项
        # self.stop_on_failure_check = QCheckBox("失败时停止")
        # self.stop_on_failure_check.setChecked(False)
        # config_layout.addWidget(self.stop_on_failure_check, 1, 0, 1, 2)
        #
        # # 重试次数设置
        # self.retry_spin = QSpinBox()
        # self.retry_spin.setRange(0, 5)
        # self.retry_spin.setValue(0)
        # config_layout.addWidget(QLabel("重试次数:"), 2, 0)
        # config_layout.addWidget(self.retry_spin, 2, 1)
        
        left_layout.addStretch()
        parent.addWidget(left_widget)
    
    def create_right_panel(self, parent):
        """创建右侧面板"""
        right_widget = QWidget()
        right_layout = QVBoxLayout(right_widget)
        
        # 创建标签页控件
        self.right_tab_widget = QTabWidget()
        right_layout.addWidget(self.right_tab_widget)
        
        # 测试控制标签页
        self.create_control_tab()
        
        # 测试结果标签页
        self.create_results_tab()
        
        parent.addWidget(right_widget)
    
    def create_control_tab(self):
        """创建测试控制标签页"""
        control_widget = QWidget()
        control_layout = QVBoxLayout(control_widget)
        
        # 测试控制组
        control_group = ModuleGroupBox("测试控制")
        control_layout.addWidget(control_group)
        
        control_inner_layout = QHBoxLayout()
        control_group.setLayout(control_inner_layout)
        
        self.start_test_btn = ControlButton("开始测试")
        self.start_test_btn.clicked.connect(self.start_automated_test)
        control_inner_layout.addWidget(self.start_test_btn)
        
        self.stop_test_btn = ControlButton("停止测试")
        self.stop_test_btn.clicked.connect(self.stop_automated_test)
        self.stop_test_btn.setEnabled(False)
        control_inner_layout.addWidget(self.stop_test_btn)
        
        # 测试进度
        progress_group = ModuleGroupBox("测试进度")
        control_layout.addWidget(progress_group)
        
        progress_layout = QVBoxLayout()
        progress_group.setLayout(progress_layout)
        
        self.test_progress = QProgressBar()
        self.test_progress.setTextVisible(True)
        progress_layout.addWidget(self.test_progress)
        
        self.current_test_label = StatusLabel("当前测试: 无")
        progress_layout.addWidget(self.current_test_label)
        
        # 测试状态
        status_group = ModuleGroupBox("测试状态")
        control_layout.addWidget(status_group)
        
        status_layout = QVBoxLayout()
        status_group.setLayout(status_layout)
        
        self.test_status_label = StatusLabel("状态: 就绪")
        status_layout.addWidget(self.test_status_label)
        
        # 测试过程日志
        process_group = ModuleGroupBox("测试过程日志")
        control_layout.addWidget(process_group)
        
        process_layout = QVBoxLayout()
        process_group.setLayout(process_layout)
        
        self.process_log_display = QTextEdit()
        self.process_log_display.setReadOnly(True)
        self.process_log_display.setMaximumHeight(200)
        self.process_log_display.setFont(QFont("Consolas", 9))
        self.process_log_display.setStyleSheet("""
            QTextEdit {
                background-color: #000000;
                color: #00FF00;
                border: 1px solid #333333;
                font-family: Consolas, Monaco, monospace;
            }
        """)
        process_layout.addWidget(self.process_log_display)
        
        control_layout.addStretch()
        self.right_tab_widget.addTab(control_widget, "测试控制")
    
    def create_results_tab(self):
        """创建测试结果标签页"""
        results_widget = QWidget()
        results_layout = QVBoxLayout(results_widget)
        
        # 结果统计
        stats_group = ModuleGroupBox("测试统计")
        results_layout.addWidget(stats_group)
        
        stats_layout = QGridLayout()
        stats_group.setLayout(stats_layout)
        
        self.total_tests_label = QLabel("总测试数: 0")
        stats_layout.addWidget(self.total_tests_label, 0, 0)
        
        self.passed_tests_label = QLabel("通过: 0")
        stats_layout.addWidget(self.passed_tests_label, 0, 1)
        
        self.failed_tests_label = QLabel("失败: 0")
        stats_layout.addWidget(self.failed_tests_label, 1, 0)
        
        self.error_tests_label = QLabel("错误: 0")
        stats_layout.addWidget(self.error_tests_label, 1, 1)
        
        self.pass_rate_label = QLabel("通过率: 0%")
        stats_layout.addWidget(self.pass_rate_label, 2, 0, 1, 2)
        
        # 详细结果表格
        detail_group = ModuleGroupBox("详细结果")
        results_layout.addWidget(detail_group)
        
        detail_layout = QVBoxLayout()
        detail_group.setLayout(detail_layout)
        
        self.results_table = QTableWidget()
        self.results_table.setColumnCount(4)
        self.results_table.setHorizontalHeaderLabels(["测试名称", "状态", "耗时(秒)", "信息"])
        self.results_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.results_table.setAlternatingRowColors(True)
        detail_layout.addWidget(self.results_table)
        
        # 导出按钮
        export_layout = QHBoxLayout()
        self.export_json_btn = QPushButton("导出JSON")
        self.export_json_btn.clicked.connect(lambda: self.export_results("json"))
        export_layout.addWidget(self.export_json_btn)
        
        self.export_csv_btn = QPushButton("导出CSV")
        self.export_csv_btn.clicked.connect(lambda: self.export_results("csv"))
        export_layout.addWidget(self.export_csv_btn)
        
        detail_layout.addLayout(export_layout)
        
        self.right_tab_widget.addTab(results_widget, "测试结果")
    
    def load_templates(self):
        """加载所有模板到下拉框"""
        self.template_combo.clear()
        template_names = self.template_manager.get_template_names()
        
        if template_names:
            self.template_combo.addItems(template_names)
            self.logger.info(f"加载了 {len(template_names)} 个测试模板")
        else:
            self.template_combo.addItem("暂无可用模板")
            self.logger.warning("未找到任何测试模板")
    
    def on_template_selected(self, template_name: str):
        """模板选择改变时的处理"""
        if template_name == "暂无可用模板":
            return
            
        template = self.template_manager.get_template(template_name)
        if template:
            self.display_template_cases(template)
            self.logger.info(f"选择了模板: {template_name}")
    
    def display_template_cases(self, template):
        """显示模板中的测试用例"""
        self.test_case_list.clear()
        
        for test_case in template.test_cases:
            item = QListWidgetItem(test_case.name)
            item.setCheckState(Qt.Checked if test_case.enabled else Qt.Unchecked)
            item.setData(Qt.UserRole, test_case)  # 存储测试用例配置
            self.test_case_list.addItem(item)

    def load_selected_template(self):
        """加载选中的模板"""
        current_template = self.template_combo.currentText()
        if current_template == "暂无可用模板":
            QMessageBox.warning(self, "警告", "请先选择一个有效的测试模板")
            return

        template = self.template_manager.get_template(current_template)
        if not template:
            QMessageBox.critical(self, "错误", f"无法加载模板: {current_template}")
            return

        # 创建测试套件
        self.current_test_suite = TestSuite(
            name=template.name,
            description=template.description
        )

        # 添加选中的测试用例
        selected_cases = self.get_selected_test_cases()
        if not selected_cases:
            QMessageBox.warning(self, "警告", "请选择至少一个测试用例")
            return

        # 初始化统计计数器
        total_selected = len(selected_cases)  # 选中总数
        success_count = 0  # 成功数
        fail_count = 0  # 失败数

        added_count = 0
        # 【修改】先清空结果表格，准备加载新的测试用例
        self.clear_test_results()
        
        for case_config in selected_cases:
            # 根据测试用例名称创建相应的测试实例
            test_instance = self.create_test_instance(case_config)
            if test_instance:
                self.current_test_suite.add_test_case(test_instance)
                added_count += 1
                success_count += 1
                # 【新增】将测试用例添加到结果表格（初始状态为 PENDING）
                self.add_test_to_results_table(case_config.name, TestStatus.PENDING, "等待执行")
            else:
                fail_count += 1
                self.logger.warning(f"测试用例 '{case_config.name}' 实例创建失败，已跳过。")

        # 构建结果信息
        result_message = (f"成功加载模板 '{template.name}'\n"
                          f"► 选中用例数: {total_selected}\n"
                          f"► 成功加载: {success_count}\n"
                          f"► 加载失败: {fail_count}")

        if success_count > 0:
            QMessageBox.information(self, "模板加载结果", result_message)
            status_msg = f"已加载 {success_count}/{total_selected} 个测试用例"
            if fail_count > 0:
                status_msg += f" ({fail_count} 个失败)"
            self.test_status_label.set_status(status_msg, True)
        else:
            QMessageBox.warning(
                self,
                "加载完成但无可用用例",
                result_message + "\n\n未能创建任何可用的测试用例实例，请检查测试类配置或日志。"
            )
            self.test_status_label.set_status("所有用例加载失败", False)
            self.current_test_suite = None  # 重置套件，因为没有可用的测试
    
    def get_selected_test_cases(self) -> List:
        """获取选中的测试用例配置"""
        selected = []
        for i in range(self.test_case_list.count()):
            item = self.test_case_list.item(i)
            if item.checkState() == Qt.Checked:
                test_case = item.data(Qt.UserRole)
                selected.append(test_case)
        return selected
    
    def create_test_instance(self, case_config):
        """根据测试用例配置创建测试实例（使用动态注册机制）"""
        # 使用配置中的test_class字段来确定测试类
        if not case_config.test_class:
            self.logger.warning(f"测试用例 '{case_config.name}' 未指定test_class")
            return None
        
        try:
            # 从全局注册中心获取测试类
            from src.auto_test import get_test_class, create_test_instance as create_instance
            
            # 检查测试类是否存在
            if not get_test_class(case_config.test_class):
                self.logger.warning(f"未找到测试类: {case_config.test_class}")
                # 尝试刷新注册中心
                from src.auto_test import test_registry
                test_registry.refresh()
                
                # 再次检查
                if not get_test_class(case_config.test_class):
                    self.logger.error(f"测试类 '{case_config.test_class}' 未注册，请检查是否正确继承BaseTestCase")
                    return None
            
            # 创建测试实例
            test_instance = create_instance(
                case_config.test_class, 
                case_config, 
                self.api_client, 
                self.logger
            )
            
            if test_instance:
                self.logger.info(f"成功创建测试实例: {case_config.test_class}")
                return test_instance
            else:
                self.logger.error(f"创建测试实例失败: {case_config.test_class}")
                return None
                
        except Exception as e:
            self.logger.error(f"创建测试实例异常: {str(e)}")
            return None
    
    def on_test_case_selection_changed(self, item):
        """测试用例选择改变时的处理"""
        # 可以在这里更新UI状态或显示详细信息
        pass
    
    def select_all_cases(self):
        """全选所有测试用例"""
        for i in range(self.test_case_list.count()):
            item = self.test_case_list.item(i)
            item.setCheckState(Qt.Checked)
    
    def deselect_all_cases(self):
        """取消选择所有测试用例"""
        for i in range(self.test_case_list.count()):
            item = self.test_case_list.item(i)
            item.setCheckState(Qt.Unchecked)
    
    def start_automated_test(self):
        """开始自动化测试"""
        if not self.current_test_suite or len(self.current_test_suite.test_cases) == 0:
            QMessageBox.warning(self, "警告", "请先加载测试模板和测试用例")
            return
        self._was_stopped_by_user = False

        if self.test_worker is not None:
            try:
                # 断开当前worker对象的所有信号连接
                self.test_worker.disconnect()
                # 如果线程仍在运行，请求停止
                if self.test_worker.isRunning():
                    self.test_worker.quit()  # 请求线程退出事件循环
                    # 可选：等待一小段时间，但不要使用wait()阻塞UI
            except Exception as e:
                self.logger.warning(f"清理旧工作线程时发生异常（通常可忽略）: {e}")
            finally:
                # 将引用置为None，让垃圾回收器回收
                self.test_worker = None


        # 更新UI状态
        self.start_test_btn.setEnabled(False)
        self.stop_test_btn.setEnabled(True)
        self.test_status_label.set_status("测试进行中...", None)
        self.current_test_label.set_status("准备开始测试...")
        self.test_progress.setValue(0)
        
        # 清空之前的测试结果
        # Deleted: 已在 load_selected_template 中清空
        
        # 创建并启动测试工作线程
        self.test_worker = AutoTestWorker(self.current_test_suite)
        self.test_worker.test_started.connect(self.on_test_started)
        self.test_worker.test_completed.connect(self.on_test_completed)
        self.test_worker.suite_completed.connect(self.on_suite_completed)
        self.test_worker.progress_updated.connect(self.on_progress_updated)
        self.test_worker.process_log_updated.connect(self.on_process_log_updated)
        self.test_worker.step_progress_updated.connect(self.on_step_progress_updated)
        self.test_worker.finished.connect(self.on_test_finished)
        self.test_worker.test_stopped.connect(self.on_test_stopped)  # 【新增】连接停止信号
        self.test_worker.start()
        
        self.logger.info(f"开始自动化测试: {self.current_test_suite.name}")
    
    def stop_automated_test(self):
        """停止自动化测试"""
        if self.test_worker and self.test_worker.isRunning():
            # 仅调用stop，不调用wait()，避免阻塞UI线程
            self.test_worker.stop()
            self.test_status_label.set_status("正在停止测试...", None)
            self.logger.info("已发送停止测试指令")
            # 禁用停止按钮，防止重复点击
            self.stop_test_btn.setEnabled(False)
        else:
            self.logger.warning("没有正在运行的测试可停止")
    
    def on_test_started(self, test_name: str):
        """测试开始时的处理"""
        self.current_test_label.set_status(f"正在执行：{test_name}")
        # 【新增】更新测试状态为 RUNNING
        self.update_test_status_in_table(test_name, TestStatus.RUNNING, "测试执行中...")
        self.logger.info(f"开始执行测试：{test_name}")
    
    def on_test_completed(self, result: TestResult):
        """测试完成时的处理"""
        # 【修改】更新已存在的测试用例结果，而不是添加新行
        self.update_test_result_in_table(result)
        self.update_test_statistics_from_results()
        self.logger.info(f"测试完成：{result.test_name} - {result.status.value}")
    
    def on_suite_completed(self, summary: dict):
        """测试套件完成时的处理"""
        self.update_test_statistics(summary)
        self.test_status_label.set_status("测试完成", True)
        self.current_test_label.set_status("所有测试已完成")
        self.logger.info(f"测试套件完成，通过率: {summary.get('pass_rate', '0%')}")
    
    def on_progress_updated(self, current: int, total: int):
        """进度更新时的处理"""
        self.test_progress.setMaximum(total)
        self.test_progress.setValue(current)
    
    def on_process_log_updated(self, level: str, message: str):
        """进程日志更新时的处理"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        
        # 根据日志级别设置不同的颜色
        color_map = {
            "INFO": "#00FF00",
            "WARNING": "#FFFF00",
            "ERROR": "#FF0000",
            "DEBUG": "#AAAAAA"
        }
        color = color_map.get(level, "#FFFFFF")
        
        # 格式化日志消息
        formatted_message = f"[{timestamp}] [{level}] {message}"
        
        # 添加到日志显示
        self.process_log_display.append(f'<span style="color: {color};">{formatted_message}</span>')
        
        # 自动滚动到底部
        scrollbar = self.process_log_display.verticalScrollBar()
        scrollbar.setValue(scrollbar.maximum())
        
        # 同时记录到主日志
        self.logger.info(f"[PROCESS] {message}")
    
    def on_step_progress_updated(self, description: str, current: int, total: int):
        """步骤进度更新时的处理"""
        # 更新当前测试标签显示步骤信息
        step_info = f"{description} ({current}/{total})"
        self.current_test_label.set_status(step_info)
    
    def on_test_finished(self):
        """测试线程结束时的处理"""
        self.start_test_btn.setEnabled(True)
        self.stop_test_btn.setEnabled(False)
        self.logger.info("自动化测试线程结束")
        # 【修改】根据用户停止标志来更新状态，不再依赖 worker 的 _is_running
        if self._was_stopped_by_user:
            self.test_status_label.set_status("测试已停止", False)  # 红色显示
        else:
            self.test_status_label.set_status("测试完成", True)  # 绿色显示

    def on_test_stopped(self):
        """【新增】处理测试被停止的信号"""
        self.logger.info("测试已被用户主动停止")
        self.process_log_display.append(
            '<span style="color: #FFA500;">[系统] 测试已被用户停止</span>'
        )
        self._was_stopped_by_user = True

        for test_name, row in self._test_row_map.items():
            # 检查当前状态，如果是 PENDING 或 RUNNING，则更新为 SKIPPED
            status_item = self.results_table.item(row, 1)
            if status_item:
                current_status_text = status_item.text()
                # 如果是待处理或运行中状态，更新为跳过
                if current_status_text in ["PENDING", "RUNNING"]:
                    self._update_status_cell(row, TestStatus.SKIPPED, "测试被用户停止")


    def add_test_result_to_table(self, result: TestResult):
        """将测试结果添加到表格（保留用于兼容）"""
        row = self.results_table.rowCount()
        self.results_table.insertRow(row)
        
        # 测试名称
        name_item = QTableWidgetItem(result.test_name)
        self.results_table.setItem(row, 0, name_item)
        
        # 状态
        status_text = result.status.value.upper()
        status_colors = {
            "PASSED": "green",
            "FAILED": "red",
            "ERROR": "orange",
            "SKIPPED": "gray"
        }
        status_color = status_colors.get(result.status.value, "black")
        status_item = QTableWidgetItem(status_text)
        status_item.setForeground(status_color)
        self.results_table.setItem(row, 1, status_item)
        
        # 耗时
        duration_item = QTableWidgetItem(f"{result.duration:.2f}")
        self.results_table.setItem(row, 2, duration_item)
        
        # 信息
        message_item = QTableWidgetItem(result.message[:100])  # 限制长度
        self.results_table.setItem(row, 3, message_item)
    
    # 【新增】添加测试用例到结果表格（初始状态）
    def add_test_to_results_table(self, test_name: str, status: TestStatus, message: str = ""):
        """添加测试用例到结果表格（初始状态或中间状态）"""
        row = self.results_table.rowCount()
        self.results_table.insertRow(row)
        
        # 保存映射关系
        self._test_row_map[test_name] = row
        
        # 测试名称
        name_item = QTableWidgetItem(test_name)
        self.results_table.setItem(row, 0, name_item)
        
        # 状态
        self._update_status_cell(row, status, message)
        
        # 耗时（初始为空）
        duration_item = QTableWidgetItem("")
        self.results_table.setItem(row, 2, duration_item)
        
        # 信息
        message_item = QTableWidgetItem(message[:100] if message else "")
        self.results_table.setItem(row, 3, message_item)
    
    # 【新增】更新测试状态
    def update_test_status_in_table(self, test_name: str, status: TestStatus, message: str = ""):
        """更新表格中指定测试的状态"""
        if test_name not in self._test_row_map:
            self.logger.warning(f"未找到测试用例：{test_name}")
            return
        
        row = self._test_row_map[test_name]
        self._update_status_cell(row, status, message)
    
    def _update_status_cell(self, row: int, status: TestStatus, message: str = ""):
        """更新状态单元格"""
        try:
            status_text = status.value.upper()
            status_colors = {
                "PENDING": QColor("gray"),
                "RUNNING": QColor("blue"),
                "PASSED": QColor("green"),
                "FAILED": QColor("red"),
                "ERROR": QColor("orange"),
                "SKIPPED": QColor("gray")
            }
            status_color = status_colors.get(status_text, "black")

            status_item = QTableWidgetItem(status_text)
            status_item.setForeground(QBrush(status_color))
            self.results_table.setItem(row, 1, status_item)

            # 更新信息列
            if message:
                message_item = QTableWidgetItem(message[:100])
                self.results_table.setItem(row, 3, message_item)
        except Exception as e:
            print(f"[CRASH] 在 _update_status_cell 中发生异常: {e}")
            import traceback
            traceback.print_exc()
            raise  # 重新抛出以便看到完整堆栈
    
    # 【新增】更新测试结果
    def update_test_result_in_table(self, result: TestResult):
        """更新表格中指定测试的最终结果"""
        if result.test_name not in self._test_row_map:
            self.logger.warning(f"未找到测试用例：{result.test_name}，将添加到表格")
            self.add_test_result_to_table(result)
            return
        
        row = self._test_row_map[result.test_name]
        
        # 更新状态
        self._update_status_cell(row, result.status, result.message)
        
        # 更新耗时
        duration_item = QTableWidgetItem(f"{result.duration:.2f}")
        self.results_table.setItem(row, 2, duration_item)

    def update_test_statistics_from_results(self):
        """从当前测试结果列表更新统计信息"""
        if not self.current_test_suite or not hasattr(self.current_test_suite, 'results'):
            return

        results = self.current_test_suite.results
        total = len(results)
        passed = len([r for r in results if r.status == TestStatus.PASSED])
        failed = len([r for r in results if r.status == TestStatus.FAILED])
        error = len([r for r in results if r.status == TestStatus.ERROR])
        skipped = len([r for r in results if r.status == TestStatus.SKIPPED])

        # 计算通过率（只计算实际执行的测试，不包括跳过的）
        executed = passed + failed + error
        pass_rate = f"{(passed / executed * 100):.1f}%" if executed > 0 else "0%"

        # 更新 UI 标签
        self.total_tests_label.setText(f"总测试数：{total}")
        self.passed_tests_label.setText(f"通过：{passed}")
        self.failed_tests_label.setText(f"失败：{failed}")
        self.error_tests_label.setText(f"错误：{error}")
        self.pass_rate_label.setText(f"通过率：{pass_rate}")

    def update_test_statistics(self, summary: dict):
        """更新测试统计信息"""
        self.total_tests_label.setText(f"总测试数: {summary.get('total_tests', 0)}")
        self.passed_tests_label.setText(f"通过: {summary.get('passed_tests', 0)}")
        self.failed_tests_label.setText(f"失败: {summary.get('failed_tests', 0)}")
        self.error_tests_label.setText(f"错误: {summary.get('error_tests', 0)}")
        self.pass_rate_label.setText(f"通过率: {summary.get('pass_rate', '0%')}")
    
    def clear_test_results(self):
        """清空测试结果"""
        self.results_table.setRowCount(0)
        self.total_tests_label.setText("总测试数: 0")
        self.passed_tests_label.setText("通过: 0")
        self.failed_tests_label.setText("失败: 0")
        self.error_tests_label.setText("错误: 0")
        self.pass_rate_label.setText("通过率: 0%")
        
        # 清空过程日志
        self.process_log_display.clear()
    
    def export_results(self, format_type: str):
        """导出测试结果"""
        if self.results_table.rowCount() == 0:
            QMessageBox.warning(self, "警告", "没有测试结果可导出")
            return
        
        # 选择保存文件
        file_filter = "JSON Files (*.json)" if format_type == "json" else "CSV Files (*.csv)"
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            f"导出{format_type.upper()}测试结果",
            f"test_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.{format_type}",
            file_filter
        )
        
        if not file_path:
            return
        
        try:
            if format_type == "json":
                self.export_results_as_json(file_path)
            else:
                self.export_results_as_csv(file_path)
            
            QMessageBox.information(self, "成功", f"测试结果已导出到: {file_path}")
            self.logger.info(f"测试结果已导出: {file_path}")
            
        except Exception as e:
            QMessageBox.critical(self, "错误", f"导出失败: {str(e)}")
            self.logger.error(f"导出测试结果失败: {str(e)}")
    
    def export_results_as_json(self, file_path: str):
        """导出为JSON格式"""
        results = []
        for row in range(self.results_table.rowCount()):
            result = {
                "test_name": self.results_table.item(row, 0).text(),
                "status": self.results_table.item(row, 1).text(),
                "duration": float(self.results_table.item(row, 2).text()),
                "message": self.results_table.item(row, 3).text()
            }
            results.append(result)
        
        data = {
            "export_time": datetime.now().isoformat(),
            "total_tests": int(self.total_tests_label.text().split(": ")[1]),
            "passed_tests": int(self.passed_tests_label.text().split(": ")[1]),
            "failed_tests": int(self.failed_tests_label.text().split(": ")[1]),
            "pass_rate": self.pass_rate_label.text().split(": ")[1],
            "results": results
        }
        
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    
    def export_results_as_csv(self, file_path: str):
        """导出为CSV格式"""
        import csv
        
        with open(file_path, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            # 写入表头
            writer.writerow(["测试名称", "状态", "耗时(秒)", "信息"])
            # 写入数据
            for row in range(self.results_table.rowCount()):
                writer.writerow([
                    self.results_table.item(row, 0).text(),
                    self.results_table.item(row, 1).text(),
                    self.results_table.item(row, 2).text(),
                    self.results_table.item(row, 3).text()
                ])
