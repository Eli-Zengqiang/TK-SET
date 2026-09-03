import sys
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QTabWidget, QWidget, QVBoxLayout, 
    QHBoxLayout, QPushButton, QLabel, QStatusBar, QMessageBox
)
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QIcon

from src.utils.config_manager import ConfigManager
from src.utils.logger import get_logger
from src.api.client import APIClient
from src.ui.individual_control_tab import IndividualControlTab
from src.ui.integrated_test_tab import IntegratedTestTab
from src.ui.auto_test_tab import AutoTestTab


class MainWindow(QMainWindow):
    """主窗口类"""
    
    def __init__(self):
        super().__init__()
        self.config_manager = ConfigManager()
        self.logger = get_logger(self.config_manager)
        self.api_client = APIClient(self.config_manager.get_server_url())
        
        # 连接状态定时器
        self.connection_timer = QTimer()
        self.connection_timer.timeout.connect(self.check_connection)
        self.connection_timer.start(30*1000)  # 每5秒检查一次
        
        self.init_ui()
        self.check_connection()
    
    def init_ui(self):
        """初始化UI"""
        self.setWindowTitle("隧道扫描仪（TK-SET） - 自动化测试客户端")
        self.setGeometry(100, 100, 1200, 800)
        
        # 创建中央部件
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # 创建主布局
        main_layout = QVBoxLayout()
        central_widget.setLayout(main_layout)
        
        # 创建标签页控件
        self.tab_widget = QTabWidget()
        main_layout.addWidget(self.tab_widget)
        
        # 创建各个标签页
        self.create_tabs()
        
        # 创建状态栏
        self.create_status_bar()
        
        # 创建工具栏按钮
        self.create_toolbar()
    
    def create_tabs(self):
        """创建标签页"""
        # 单个模块功能控制标签页
        self.individual_control_tab = IndividualControlTab(self.api_client, self.config_manager)
        self.tab_widget.addTab(self.individual_control_tab, "单模块控制")
        
        # 集成模块化测试标签页
        self.integrated_test_tab = IntegratedTestTab(self.api_client, self.config_manager)
        self.tab_widget.addTab(self.integrated_test_tab, "集成测试")
        
        # 自动化测试标签页
        self.auto_test_tab = AutoTestTab(self.api_client, self.config_manager)
        self.tab_widget.addTab(self.auto_test_tab, "自动化测试")
    
    def create_status_bar(self):
        """创建状态栏"""
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        
        # 连接状态标签
        self.connection_label = QLabel("连接状态: 未知")
        self.status_bar.addPermanentWidget(self.connection_label)
        
        # 服务器地址标签
        server_url = self.config_manager.get_server_url()
        self.server_label = QLabel(f"服务器: {server_url}")
        self.status_bar.addPermanentWidget(self.server_label)
    
    def create_toolbar(self):
        """创建工具栏"""
        toolbar = self.addToolBar("主工具栏")
        
        # 连接测试按钮
        connect_btn = QPushButton("测试连接")
        connect_btn.clicked.connect(self.test_connection)
        toolbar.addWidget(connect_btn)
        
        # 刷新按钮
        refresh_btn = QPushButton("刷新状态")
        refresh_btn.clicked.connect(self.refresh_all_tabs)
        toolbar.addWidget(refresh_btn)
        
        # 分隔符
        toolbar.addSeparator()
        
        # 关于按钮
        about_btn = QPushButton("关于")
        about_btn.clicked.connect(self.show_about)
        toolbar.addWidget(about_btn)
    
    def check_connection(self):
        """检查服务器连接状态"""
        try:
            result = self.api_client.ping()
            if result.get("message")=='pong':
                self.connection_label.setText("连接状态: ✓ 已连接")
                self.connection_label.setStyleSheet("color: green;")
                self.logger.info("服务器连接正常")
            else:
                self.connection_label.setText("连接状态: ✗ 连接失败")
                self.connection_label.setStyleSheet("color: red;")
                self.logger.warning("服务器连接失败")
        except Exception as e:
            self.connection_label.setText("连接状态: ✗ 连接异常")
            self.connection_label.setStyleSheet("color: red;")
            self.logger.error(f"连接检查异常: {str(e)}")
    
    def test_connection(self):
        """手动测试连接"""
        sender = self.sender()
        if sender:
            sender.setEnabled(False)
        
        self.logger.info("手动测试服务器连接")
        try:
            result = self.api_client.get_system_info()
            if result.get("success", False):
                QMessageBox.information(
                    self, 
                    "连接成功", 
                    f"服务器连接正常\n系统信息: {result.get('data', 'Unknown')}"
                )
            else:
                QMessageBox.warning(
                    self, 
                    "连接失败", 
                    f"无法连接到服务器\n错误: {result.get('message', 'Unknown error')}"
                )
        except Exception as e:
            QMessageBox.critical(
                self, 
                "连接异常", 
                f"连接测试出现异常\n错误: {str(e)}"
            )
        finally:
            if sender:
                sender.setEnabled(True)
    
    def refresh_all_tabs(self):
        """刷新所有标签页"""
        self.logger.info("刷新所有标签页")
        self.individual_control_tab.refresh()
        self.integrated_test_tab.refresh()
        #self.auto_test_tab.refresh()
        self.check_connection()
    
    def disable_all_buttons_temporarily(self, duration_ms=1000):
        """临时禁用所有按钮，防止快速连续点击"""
        # 禁用工具栏按钮
        for i in range(self.toolBar().layout().count()):
            widget = self.toolBar().layout().itemAt(i).widget()
            if isinstance(widget, QPushButton):
                widget.setEnabled(False)
        
        # 启动定时器恢复按钮
        QTimer.singleShot(duration_ms, self.enable_all_buttons)
    
    def enable_all_buttons(self):
        """启用所有按钮"""
        # 启用工具栏按钮
        for i in range(self.toolBar().layout().count()):
            widget = self.toolBar().layout().itemAt(i).widget()
            if isinstance(widget, QPushButton):
                widget.setEnabled(True)
    
    def show_about(self):
        """显示关于对话框"""
        sender = self.sender()
        if sender:
            sender.setEnabled(False)
            
        QMessageBox.about(
            self,
            "关于 Auto Test Client",
            """<h3>Auto Test Client v1.0</h3>
            <p>自动化测试客户端</p>
            <p>用于控制和测试硬件设备</p>
            <p><b>功能特点:</b></p>
            <ul>
                <li>单模块功能控制</li>
                <li>集成模块化测试</li>
                <li>自动化测试报告生成</li>
                <li>实时状态监控</li>
            </ul>
            <p>© 2026 Auto Test Team</p>"""
        )
        
        if sender:
            sender.setEnabled(True)
    
    def closeEvent(self, event):
        """窗口关闭事件"""
        self.logger.info("客户端程序即将关闭")
        self.connection_timer.stop()
        event.accept()


def main():
    """主函数"""
    app = QApplication(sys.argv)
    
    # 设置应用程序属性
    app.setApplicationName("Auto Test Client")
    app.setApplicationVersion("1.0")
    app.setOrganizationName("Auto Test Team")
    
    # 创建并显示主窗口
    window = MainWindow()
    window.show()
    
    # 运行应用程序
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()