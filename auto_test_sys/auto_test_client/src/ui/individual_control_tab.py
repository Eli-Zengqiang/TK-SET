from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGridLayout, QScrollArea,
    QTabWidget, QSplitter, QFrame, QPushButton
)
from PyQt5.QtCore import Qt, QThread, pyqtSignal
import json
from datetime import datetime

from src.ui.components import (
    ModuleGroupBox, ControlButton, StatusLabel, ResultDisplay,
    ParameterInput
)
from src.utils.logger import get_logger


class APITestThread(QThread):
    """API测试线程"""
    result_ready = pyqtSignal(dict, str)  # 结果信号: (result_dict, test_name)
    
    def __init__(self, api_method, *args, **kwargs):
        super().__init__()
        self.api_method = api_method
        self.args = args
        self.kwargs = kwargs
    
    def run(self):
        try:
            result = self.api_method(*self.args, **self.kwargs)
            test_name = self.api_method.__name__
            self.result_ready.emit(result, test_name)
        except Exception as e:
            error_result = {
                "success": False,
                "message": f"执行异常: {str(e)}",
                "error": str(e)
            }
            test_name = getattr(self.api_method, '__name__', 'Unknown')
            self.result_ready.emit(error_result, test_name)


class IndividualControlTab(QWidget):
    """单个模块功能控制标签页"""
    
    def __init__(self, api_client, config_manager, parent=None):
        super().__init__(parent)
        self.api_client = api_client
        self.config_manager = config_manager
        self.logger = get_logger(config_manager)
        self.test_threads = []  # 管理测试线程
        self.active_buttons = {}  # 记录正在执行的按钮
        
        self.init_ui()
    
    def init_ui(self):
        """初始化UI"""
        main_layout = QVBoxLayout(self)
        
        # 创建分割器
        splitter = QSplitter(Qt.Horizontal)
        main_layout.addWidget(splitter)
        
        # 左侧模块选择区域
        self.create_module_selector(splitter)
        
        # 右侧控制面板
        self.create_control_panel(splitter)
        
        # 设置分割比例
        splitter.setSizes([200, 800])
    
    def create_module_selector(self, parent):
        """创建模块选择区域"""
        selector_widget = QWidget()
        selector_layout = QVBoxLayout(selector_widget)
        
        # 模块选择标签
        selector_title = ModuleGroupBox("功能模块")
        selector_layout.addWidget(selector_title)
        
        # 模块按钮布局
        modules_layout = QVBoxLayout()
        selector_title.setLayout(modules_layout)
        
        # 获取启用的模块
        enabled_modules = self.config_manager.get_enabled_modules()
        
        # 为每个模块创建按钮
        self.module_buttons = {}
        for module_name, config in enabled_modules.items():
            btn = ControlButton(config.get("name", module_name))
            btn.clicked.connect(lambda checked, m=module_name: self.switch_module(m))
            self.module_buttons[module_name] = btn
            modules_layout.addWidget(btn)
        
        modules_layout.addStretch()  # 添加弹性空间
        parent.addWidget(selector_widget)
    
    def create_control_panel(self, parent):
        """创建控制面板"""
        self.control_panel = QTabWidget()
        
        # 创建各个功能标签页
        self.create_power_control_tab()
        self.create_config_control_tab()  # <- 新增的配置管理页
        self.create_motor_control_tab()
        self.create_camera_control_tab()
        self.create_lidar_control_tab()
        self.create_inclinometer_control_tab()
        self.create_led_control_tab()
        self.create_system_info_tab()
        
        parent.addWidget(self.control_panel)
    
    def create_power_control_tab(self):
        """创建电源控制标签页"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # 电源控制组
        power_group = ModuleGroupBox("电源管理")
        layout.addWidget(power_group)
        
        power_layout = QGridLayout()
        power_group.setLayout(power_layout)
        
        # 模块选择
        self.power_module_combo = ParameterInput("模块", "combo")
        modules = self.config_manager.get("modules.power.modules", [])
        for module in modules:
            self.power_module_combo.input_widget.addItem(module)
        power_layout.addWidget(self.power_module_combo, 0, 0, 1, 2)
        
        # 控制按钮
        self.power_on_btn = ControlButton("上电")
        self.power_on_btn.clicked.connect(self.power_on_module)
        power_layout.addWidget(self.power_on_btn, 1, 0)
        
        self.power_off_btn = ControlButton("断电")
        self.power_off_btn.clicked.connect(self.power_off_module)
        power_layout.addWidget(self.power_off_btn, 1, 1)
        
        # 状态查询
        self.power_status_btn = ControlButton("查询状态")
        self.power_status_btn.clicked.connect(self.get_power_status)
        power_layout.addWidget(self.power_status_btn, 2, 0, 1, 2)
        
        # 批量控制
        batch_group = ModuleGroupBox("批量控制")
        layout.addWidget(batch_group)
        
        batch_layout = QHBoxLayout()
        batch_group.setLayout(batch_layout)
        
        self.power_on_all_btn = ControlButton("全部上电")
        self.power_on_all_btn.clicked.connect(self.power_on_all_modules)
        batch_layout.addWidget(self.power_on_all_btn)
        
        self.power_off_all_btn = ControlButton("全部断电")
        self.power_off_all_btn.clicked.connect(self.power_off_all_modules)
        batch_layout.addWidget(self.power_off_all_btn)

        self.power_all_status_btn = ControlButton("全部模块状态")
        self.power_all_status_btn.clicked.connect(self.power_all_status)
        batch_layout.addWidget(self.power_all_status_btn)
        
        # 状态显示
        self.power_status_label = StatusLabel("电源状态: 未知")
        layout.addWidget(self.power_status_label)
        
        # 结果显示
        self.power_result_display = ResultDisplay()
        layout.addWidget(self.power_result_display)
        
        layout.addStretch()
        self.control_panel.addTab(tab, "电源管理")

    def update_current_time_display(self):
        """‘更新为当前时间’按钮的槽函数：刷新时间输入框的显示值为当前系统时间"""
        current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        self.time_input.set_value(current_time)
        # 可以可选地在日志或状态栏显示一条消息，但非必须
        self.logger.info(f"已更新目标时间显示为：{current_time}")

    def create_config_control_tab(self):
        """创建配置管理标签页"""
        tab = QWidget()
        layout = QVBoxLayout(tab)

        # === Wi-Fi 配置 ===
        wifi_group = ModuleGroupBox("Wi-Fi 配置")
        layout.addWidget(wifi_group)

        wifi_layout = QVBoxLayout()
        wifi_group.setLayout(wifi_layout)

        self.wifi_setup_btn = ControlButton("设置Wi-Fi SSID")
        self.wifi_setup_btn.clicked.connect(self.config_wifi_setup)
        wifi_layout.addWidget(self.wifi_setup_btn)

        # === 系统时间同步 ===
        time_group = ModuleGroupBox("系统时间同步")
        layout.addWidget(time_group)

        time_layout = QGridLayout()
        time_group.setLayout(time_layout)

        self.time_input = ParameterInput("目标时间 (YYYY-MM-DD HH:MM:SS)", "text")
        current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        self.time_input.set_value(current_time)  # 示例时间
        time_layout.addWidget(self.time_input, 0, 0, 1, 3)

        # 更新按钮（第二行，第一列）
        self.time_update_btn = ControlButton('更新时间')
        self.time_update_btn.clicked.connect(self.update_current_time_display)
        time_layout.addWidget(self.time_update_btn, 1, 0)

        self.time_sync_btn = ControlButton("同步系统时间")
        self.time_sync_btn.clicked.connect(self.config_sync_time)
        time_layout.addWidget(self.time_sync_btn, 1, 1, 1, 2)

        # === 硬件模块配置 ===
        hardware_group = ModuleGroupBox("硬件模块配置")
        layout.addWidget(hardware_group)

        hardware_layout = QVBoxLayout()
        hardware_group.setLayout(hardware_layout)

        # 各模块独立配置按钮
        hw_grid_layout = QGridLayout()
        self.motor_config_btn = ControlButton("配置转台")
        self.motor_config_btn.clicked.connect(self.config_motor_setting)
        hw_grid_layout.addWidget(self.motor_config_btn, 0, 0)

        self.min_motor_config_btn = ControlButton("配置小电机")
        self.min_motor_config_btn.clicked.connect(self.config_min_motor_setting)
        hw_grid_layout.addWidget(self.min_motor_config_btn, 0, 1)

        self.lidar_config_btn = ControlButton("配置雷达")
        self.lidar_config_btn.clicked.connect(self.config_lidar_setup)
        hw_grid_layout.addWidget(self.lidar_config_btn, 1, 0)

        hardware_layout.addLayout(hw_grid_layout)

        # 一键配置所有硬件
        self.all_devices_setup_btn = ControlButton("一键配置所有硬件")
        self.all_devices_setup_btn.clicked.connect(self.config_setup_all_devices)
        hardware_layout.addWidget(self.all_devices_setup_btn)

        # === 状态与结果显示区域 ===
        self.config_status_label = StatusLabel("配置状态: 未知")
        layout.addWidget(self.config_status_label)

        self.config_result_display = ResultDisplay()
        layout.addWidget(self.config_result_display)

        layout.addStretch()
        self.control_panel.addTab(tab, "配置管理")

    def create_motor_control_tab(self):
        """创建电机控制标签页"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # 转台电机控制
        turret_group = ModuleGroupBox("转台电机控制")
        layout.addWidget(turret_group)
        
        turret_layout = QGridLayout()
        turret_group.setLayout(turret_layout)
        
        # 找零位
        self.find_zero_btn = ControlButton("找零位")
        self.find_zero_btn.clicked.connect(self.motor_find_zero)
        turret_layout.addWidget(self.find_zero_btn, 0, 0, 1, 2)
        
        # 读取当前角度
        self.get_angle_btn = ControlButton("读取当前角度")
        self.get_angle_btn.clicked.connect(self.motor_get_angle)
        turret_layout.addWidget(self.get_angle_btn, 1, 0, 1, 2)
        
        # 位置设置
        self.position_input = ParameterInput("目标位置 (°)", "decimal")
        self.position_input.set_value(90.0)
        turret_layout.addWidget(self.position_input, 2, 0, 1, 2)
                
        self.set_position_btn = ControlButton("设置位置")
        self.set_position_btn.clicked.connect(self.motor_set_position)
        turret_layout.addWidget(self.set_position_btn, 3, 0, 1, 2)
                
        # 速度设置
        self.speed_input = ParameterInput("速度 (°/s)", "decimal")
        self.speed_input.set_value(5.0)
        turret_layout.addWidget(self.speed_input, 4, 0)
                
        self.set_speed_btn = ControlButton("设置速度")
        self.set_speed_btn.clicked.connect(self.motor_set_speed)
        turret_layout.addWidget(self.set_speed_btn, 4, 1)
        
        # 小电机控制
        mini_group = ModuleGroupBox("小电机控制")
        layout.addWidget(mini_group)
        
        mini_layout = QGridLayout()
        mini_group.setLayout(mini_layout)
        
        # # 角度设置
        # self.mini_angle_input = ParameterInput("目标角度(°)", "decimal")
        # self.mini_angle_input.set_value(45.0)
        # mini_layout.addWidget(self.mini_angle_input, 0, 0, 1, 2)
        #
        # self.set_mini_angle_btn = ControlButton("设置角度")
        # self.set_mini_angle_btn.clicked.connect(self.mini_motor_set_angle)
        # mini_layout.addWidget(self.set_mini_angle_btn, 1, 0, 1, 2)
        
        # 获取小电机限位角度
        self.detect_limits_btn = ControlButton("获取小电机限位角度")
        self.detect_limits_btn.clicked.connect(self.mini_motor_detect_limits)
        mini_layout.addWidget(self.detect_limits_btn, 2, 0, 1, 2)
        
        # 相对移动
        self.delta_angle_input = ParameterInput("相对角度 (°)", "decimal")
        self.delta_angle_input.set_value(15.0)
        mini_layout.addWidget(self.delta_angle_input, 3, 0)
                
        self.relative_move_btn = ControlButton("相对移动")
        self.relative_move_btn.clicked.connect(self.mini_motor_relative_move)
        mini_layout.addWidget(self.relative_move_btn, 3, 1)
                
        # 绝对位置设定（新增）
        self.absolute_angle_input = ParameterInput("绝对位置 (°)", "decimal")
        self.absolute_angle_input.set_value(45.0)
        mini_layout.addWidget(self.absolute_angle_input, 4, 0)
                
        self.set_absolute_pos_btn = ControlButton("设定绝对位置")
        self.set_absolute_pos_btn.clicked.connect(self.mini_motor_set_angle)
        mini_layout.addWidget(self.set_absolute_pos_btn, 4, 1)
                
        # 读取角度
        self.read_angle_btn = ControlButton("读取当前角度")
        self.read_angle_btn.clicked.connect(self.mini_motor_read_angle)
        mini_layout.addWidget(self.read_angle_btn, 5, 0, 1, 2)
        
        # 状态显示
        self.motor_status_label = StatusLabel("电机状态: 未知")
        layout.addWidget(self.motor_status_label)
        
        # 结果显示
        self.motor_result_display = ResultDisplay()
        layout.addWidget(self.motor_result_display)
        
        layout.addStretch()
        self.control_panel.addTab(tab, "电机控制")
    
    def create_camera_control_tab(self):
        """创建相机控制标签页"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # 相机参数设置
        camera_group = ModuleGroupBox("相机控制")
        layout.addWidget(camera_group)
        
        camera_layout = QGridLayout()
        camera_group.setLayout(camera_layout)
        
        # 设备选择
        self.camera_device_input = ParameterInput("设备路径", "text")
        self.camera_device_input.set_value("/dev/video0")
        camera_layout.addWidget(self.camera_device_input, 0, 0, 1, 2)
        
        # 分辨率选择
        self.resolution_combo = ParameterInput("分辨率", "combo")
        resolutions = self.config_manager.get("modules.camera.resolutions", [])
        for res in resolutions:
            self.resolution_combo.input_widget.addItem(res)
        camera_layout.addWidget(self.resolution_combo, 1, 0, 1, 2)
        
        # 文件名设置
        self.filename_input = ParameterInput("文件名", "text")
        self.filename_input.set_value("test_image.jpg")
        camera_layout.addWidget(self.filename_input, 2, 0, 1, 2)
        
        # 控制按钮
        self.set_resolution_btn = ControlButton("设置分辨率")
        self.set_resolution_btn.clicked.connect(self.camera_set_resolution)
        camera_layout.addWidget(self.set_resolution_btn, 3, 0)
        
        self.capture_btn = ControlButton("拍照")
        self.capture_btn.clicked.connect(self.camera_capture)
        camera_layout.addWidget(self.capture_btn, 3, 1)
        
        self.set_and_capture_btn = ControlButton("设置并拍照")
        self.set_and_capture_btn.clicked.connect(self.camera_set_and_capture)
        camera_layout.addWidget(self.set_and_capture_btn, 4, 0, 1, 2)
        
        # 下载按钮和打开文件夹按钮
        download_layout = QHBoxLayout()
        
        self.download_image_btn = ControlButton("下载图片文件")
        self.download_image_btn.clicked.connect(self.camera_download_image)
        download_layout.addWidget(self.download_image_btn)
        
        # 打开文件夹按钮
        self.open_folder_btn = QPushButton("📁")  # 使用文件夹图标
        self.open_folder_btn.setToolTip("打开下载文件夹")
        self.open_folder_btn.setMaximumWidth(40)  # 设置较小的宽度
        self.open_folder_btn.clicked.connect(self.open_download_folder)
        # 设置按钮样式使其更小
        self.open_folder_btn.setStyleSheet("""
            QPushButton {
                font-size: 12px;
                padding: 2px;
                margin: 1px;
                border: 1px solid #ccc;
                border-radius: 3px;
                background-color: #f0f0f0;
            }
            QPushButton:hover {
                background-color: #e0e0e0;
            }
            QPushButton:pressed {
                background-color: #d0d0d0;
            }
        """)
        download_layout.addWidget(self.open_folder_btn)
        
        # 将水平布局添加到网格布局中
        camera_layout.addLayout(download_layout, 5, 0, 1, 2)
        
        # 状态显示
        self.camera_status_label = StatusLabel("相机状态: 未知")
        layout.addWidget(self.camera_status_label)
        
        # 结果显示
        self.camera_result_display = ResultDisplay()
        layout.addWidget(self.camera_result_display)
        
        layout.addStretch()
        self.control_panel.addTab(tab, "相机控制")
    
    def create_led_control_tab(self):
        """创建LED控制标签页"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # LED控制组
        # led_group = ModuleGroupBox("LED控制")
        # layout.addWidget(led_group)
        #
        # led_layout = QVBoxLayout()
        # led_group.setLayout(led_layout)
        
        # 颜色选择
        # self.led_color_combo = ParameterInput("预设颜色", "combo")
        # colors = self.config_manager.get("modules.led.colors", [])
        # for color in colors:
        #     self.led_color_combo.input_widget.addItem(color)
        # led_layout.addWidget(self.led_color_combo)
        
        # # 预设颜色按钮
        # preset_layout = QHBoxLayout()
        # self.set_led_color_btn = ControlButton("设置预设颜色")
        # self.set_led_color_btn.clicked.connect(self.led_set_color)
        # preset_layout.addWidget(self.set_led_color_btn)
        #
        # self.turn_off_led_btn = ControlButton("关闭LED")
        # self.turn_off_led_btn.clicked.connect(self.led_turn_off)
        # preset_layout.addWidget(self.turn_off_led_btn)
        # led_layout.addLayout(preset_layout)
        
        # 自定义颜色
        custom_group = ModuleGroupBox("LED控制")
        layout.addWidget(custom_group)
        
        custom_layout = QGridLayout()
        custom_group.setLayout(custom_layout)
        
        self.red_input = ParameterInput("红色", "number")
        self.red_input.set_value(255)
        custom_layout.addWidget(self.red_input, 0, 0)
        
        self.green_input = ParameterInput("绿色", "number")
        self.green_input.set_value(0)
        custom_layout.addWidget(self.green_input, 0, 1)
        
        self.blue_input = ParameterInput("蓝色", "number")
        self.blue_input.set_value(0)
        custom_layout.addWidget(self.blue_input, 0, 2)
        
        self.set_custom_color_btn = ControlButton("设置自定义颜色")
        self.set_custom_color_btn.clicked.connect(self.led_set_custom_color)
        custom_layout.addWidget(self.set_custom_color_btn, 1, 0, 1, 3)
        
        # 状态显示
        self.led_status_label = StatusLabel("LED状态: 未知")
        layout.addWidget(self.led_status_label)
        
        # 结果显示
        self.led_result_display = ResultDisplay()
        layout.addWidget(self.led_result_display)
        
        layout.addStretch()
        self.control_panel.addTab(tab, "LED控制")
    
    def create_lidar_control_tab(self):
        """创建雷达控制标签页"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # 雷达基本信息
        info_group = ModuleGroupBox("雷达基本信息")
        layout.addWidget(info_group)
        
        info_layout = QGridLayout()
        info_group.setLayout(info_layout)
        
        # 获取雷达信息按钮
        self.lidar_sn_btn = ControlButton("获取序列号")
        self.lidar_sn_btn.clicked.connect(self.lidar_get_sn)
        info_layout.addWidget(self.lidar_sn_btn, 0, 0)
        
        self.lidar_calib_btn = ControlButton("获取校准数据")
        self.lidar_calib_btn.clicked.connect(self.lidar_get_calibration)
        info_layout.addWidget(self.lidar_calib_btn, 0, 1)
        
        # 雷达设置
        # setup_group = ModuleGroupBox("雷达设置")
        # layout.addWidget(setup_group)
        #
        # setup_layout = QGridLayout()
        # setup_group.setLayout(setup_layout)
        #
        # # 初始化设置
        # self.lidar_setup_btn = ControlButton("初始化设置")
        # self.lidar_setup_btn.clicked.connect(self.lidar_setup)
        # setup_layout.addWidget(self.lidar_setup_btn, 0, 0, 1, 2)
        
        # 状态显示
        self.lidar_status_label = StatusLabel("雷达状态: 未知")
        layout.addWidget(self.lidar_status_label)
        
        # 结果显示
        self.lidar_result_display = ResultDisplay()
        layout.addWidget(self.lidar_result_display)
        
        layout.addStretch()
        self.control_panel.addTab(tab, "雷达控制")
    
    def create_inclinometer_control_tab(self):
        """创建倾角仪控制标签页"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # 倾角仪数据读取
        read_group = ModuleGroupBox("倾角仪数据读取")
        layout.addWidget(read_group)
        
        read_layout = QGridLayout()
        read_group.setLayout(read_layout)
        
        # 读取当前数据
        self.inc_read_btn = ControlButton("读取当前数据")
        self.inc_read_btn.clicked.connect(self.inclinometer_read)
        read_layout.addWidget(self.inc_read_btn, 0, 0, 1, 2)

        # 状态显示
        self.inclinometer_status_label = StatusLabel("倾角仪状态: 未知")
        layout.addWidget(self.inclinometer_status_label)
        
        # 结果显示
        self.inclinometer_result_display = ResultDisplay()
        layout.addWidget(self.inclinometer_result_display)
        
        layout.addStretch()
        self.control_panel.addTab(tab, "倾角仪控制")
    
    def create_system_info_tab(self):
        """创建系统信息标签页"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # 系统信息组
        info_group = ModuleGroupBox("系统信息")
        layout.addWidget(info_group)
        
        info_layout = QVBoxLayout()
        info_group.setLayout(info_layout)
        
        # 查询按钮
        self.system_info_btn = ControlButton("获取系统信息")
        self.system_info_btn.clicked.connect(self.get_system_info)
        info_layout.addWidget(self.system_info_btn)
        
        self.system_metrics_btn = ControlButton("获取系统指标")
        self.system_metrics_btn.clicked.connect(self.get_system_metrics)
        info_layout.addWidget(self.system_metrics_btn)
        
        self.battery_status_btn = ControlButton("获取电池状态")
        self.battery_status_btn.clicked.connect(self.get_battery_status)
        info_layout.addWidget(self.battery_status_btn)
        
        self.tf_card_btn = ControlButton("获取TF卡状态")
        self.tf_card_btn.clicked.connect(self.get_tf_card_status)
        info_layout.addWidget(self.tf_card_btn)
        
        # 状态显示
        self.system_status_label = StatusLabel("系统状态: 未知")
        layout.addWidget(self.system_status_label)
        
        # 结果显示
        self.system_result_display = ResultDisplay()
        layout.addWidget(self.system_result_display)
        
        layout.addStretch()
        self.control_panel.addTab(tab, "系统信息")
    
    # === 电源控制方法 ===
    def power_on_module(self):
        module = self.power_module_combo.get_value()
        self.execute_api_call(self.api_client.power_on, "电源上电", module)
    
    def power_off_module(self):
        module = self.power_module_combo.get_value()
        self.execute_api_call(self.api_client.power_off, "电源断电", module)
    
    def get_power_status(self):
        module = self.power_module_combo.get_value()
        self.execute_api_call(self.api_client.get_power_status, "查询电源状态", module)

    def power_all_status(self):
        self.execute_api_call(self.api_client.get_devices_status, "查询全部模块电源状态")

    def power_on_all_modules(self):
        self.execute_api_call(self.api_client.power_on_all, "全部模块上电")
    
    def power_off_all_modules(self):
        self.execute_api_call(self.api_client.power_off_all, "全部模块断电")

    # === 配置管理方法 ===
    def config_wifi_setup(self):
        """配置Wi-Fi SSID"""
        self.execute_api_call(self.api_client.wifi_setup, "配置Wi-Fi")

    def config_sync_time(self):
        """同步系统时间"""
        target_time = self.time_input.get_value()
        self.execute_api_call(self.api_client.sync_system_time, "同步系统时间", target_time)

    def config_motor_setting(self):
        """配置转台参数"""
        self.execute_api_call(self.api_client.motor_configure, "配置转台")

    def config_min_motor_setting(self):
        """配置小电机参数"""
        self.execute_api_call(self.api_client.min_motor_configure, "配置小电机")

    def config_lidar_setup(self):
        """雷达初始化设置"""
        self.execute_api_call(self.api_client.lidar_setup, "配置雷达")

    def config_setup_all_devices(self):
        """一键配置所有硬件"""
        self.execute_api_call(self.api_client.setup_all_devices, "一键配置所有硬件")




    # === 电机控制方法 ===
    def motor_find_zero(self):
        self.execute_api_call(self.api_client.motor_find_zero, "转台找零位", 60)
    
    def motor_set_position(self):
        position = self.position_input.get_value()
        self.execute_api_call(self.api_client.motor_set_position, "设置转台位置", position, 60)
    
    def motor_set_speed(self):
        speed = self.speed_input.get_value()
        self.execute_api_call(self.api_client.motor_set_speed, "设置转台速度", speed)
    
    def motor_get_angle(self):
        self.execute_api_call(self.api_client.motor_get_angle, "读取转台当前角度", 60)
    
    def mini_motor_set_angle(self):
        angle = self.absolute_angle_input.get_value()
        self.execute_api_call(self.api_client.min_motor_set_angle, "设置小电机角度", angle, 60)
    
    def mini_motor_relative_move(self):
        delta_angle = self.delta_angle_input.get_value()
        self.execute_api_call(self.api_client.min_motor_relative_move, "小电机相对移动", delta_angle, 30)
    
    def mini_motor_read_angle(self):
        self.execute_api_call(self.api_client.min_motor_read_angle, "读取小电机角度")
    
    def mini_motor_detect_limits(self):
        self.execute_api_call(self.api_client.min_motor_detect_limits, "获取小电机限位角度", 300, 100)
    
    # === 相机控制方法 ===
    def camera_set_resolution(self):
        device = self.camera_device_input.get_value()
        mode = self.resolution_combo.get_value()
        self.execute_api_call(self.api_client.camera_set_resolution, "设置相机分辨率", device, mode)
    
    def camera_capture(self):
        device = self.camera_device_input.get_value()
        filename = self.filename_input.get_value()
        self.execute_api_call(self.api_client.camera_capture, "相机拍照", device, filename)
    
    def camera_set_and_capture(self):
        device = self.camera_device_input.get_value()
        mode = self.resolution_combo.get_value()
        filename = self.filename_input.get_value()
        self.execute_api_call(self.api_client.camera_set_and_capture, "设置并拍照", device, mode, filename)
    
    def camera_download_image(self):
        """下载图片文件"""
        filename = self.filename_input.get_value()
        if not filename:
            self.camera_result_display.append_result("请先设置文件名", False)
            self.camera_status_label.set_status("下载失败: 未设置文件名", False)
            return
        
        # 获取下载保存路径
        download_path = self.config_manager.get("download.save_path", "downloads")
        import os
        # 确保路径是绝对路径
        if not os.path.isabs(download_path):
            # 获取当前工作目录
            current_dir = os.getcwd()
            download_path = os.path.join(current_dir, download_path)
        
        save_path = os.path.join(download_path, filename)
        
        self.logger.info(f"准备下载文件: {filename} 到 {save_path}")
        # 显示开始下载的状态
        self.camera_result_display.append_result(f"开始下载文件: {filename}", None)
        self.camera_status_label.set_status("下载中...", None)
        self.execute_api_call(self.api_client.download_file, "下载图片文件", filename, save_path)
    
    def open_download_folder(self):
        """打开下载文件夹"""
        try:
            # 获取下载路径
            download_path = self.config_manager.get("download.save_path", "downloads")
            import os
            # 确保路径是绝对路径
            if not os.path.isabs(download_path):
                current_dir = os.getcwd()
                download_path = os.path.join(current_dir, download_path)
            
            # 确保目录存在
            if not os.path.exists(download_path):
                os.makedirs(download_path)
                self.camera_result_display.append_result(f"创建下载目录: {download_path}", True)
            
            # 根据操作系统打开文件夹
            import platform
            system = platform.system()
            
            if system == "Windows":
                os.startfile(download_path)
            elif system == "Darwin":  # macOS
                os.system(f"open '{download_path}'")
            else:  # Linux
                os.system(f"xdg-open '{download_path}'")
                
            self.camera_result_display.append_result(f"已打开下载文件夹: {download_path}", True)
            self.logger.info(f"打开下载文件夹: {download_path}")
            
        except Exception as e:
            error_msg = f"打开文件夹失败: {str(e)}"
            self.camera_result_display.append_result(error_msg, False)
            self.logger.error(error_msg)
    
    # === LED控制方法 ===
    
    def led_set_custom_color(self):
        red = self.red_input.get_value()
        green = self.green_input.get_value()
        blue = self.blue_input.get_value()
        self.execute_api_call(self.api_client.led_set_custom_color, "设置自定义LED颜色", red, green, blue)


    # === 倾角仪控制方法 ===
    def inclinometer_read(self):
        self.execute_api_call(self.api_client.inclinometer_read, "读取倾角仪数据")

    # === 雷达控制方法 ===
    def lidar_get_sn(self):
        self.execute_api_call(self.api_client.lidar_get_sn, "获取雷达序列号")

    def lidar_get_calibration(self):
        self.execute_api_call(self.api_client.lidar_get_calibration, "获取雷达校准参数")

    # def lidar_setup(self):
    #     self.execute_api_call(self.api_client.lidar_setup, "雷达初始化配置")

    # === 系统信息方法 ===
    def get_system_info(self):
        self.execute_api_call(self.api_client.get_system_info, "获取系统信息")
    
    def get_system_metrics(self):
        self.execute_api_call(self.api_client.get_system_metrics, "获取系统指标")
    
    def get_battery_status(self):
        self.execute_api_call(self.api_client.get_battery_status, "获取电池状态")
    
    def get_tf_card_status(self):
        self.execute_api_call(self.api_client.get_tf_card_status, "获取TF卡状态")
    
    def execute_api_call(self, api_method, display_name="", *args):
        """执行API调用"""
        # 创建并启动测试线程
        thread = APITestThread(api_method, *args)
        thread.result_ready.connect(lambda result, name: self.handle_api_result(result, name, display_name))
        thread.finished.connect(lambda: self._on_thread_finished(thread, api_method))
        thread.start()
        
        # 保存线程引用
        self.test_threads.append(thread)
        
        # 禁用相关按钮
        self._disable_related_buttons(api_method, display_name)
        
        # 更新状态显示
        if hasattr(self, f"{api_method.__name__.replace('api_client.', '')}_status_label"):
            status_label = getattr(self, f"{api_method.__name__.replace('api_client.', '')}_status_label")
            status_label.set_status("执行中...", None)
    
    def handle_api_result(self, result, method_name, display_name):
        """处理API结果"""
        self.logger.info(f"API调用结果 - {display_name}: {result}")
        
        # 找到对应的显示组件
        result_display = None
        status_label = None
        
        # 根据方法名确定对应的显示组件
        if 'power' in method_name or 'devices_status' in method_name:
            result_display = self.power_result_display
            status_label = self.power_status_label
        elif 'wifi' in method_name or 'sync' in method_name or 'motor_configure' in method_name or 'lidar_setup' in method_name or 'setup_all' in method_name:
            # 新增：处理所有配置相关的API结果
            result_display = self.config_result_display
            status_label = self.config_status_label
        elif 'motor' in method_name:
            result_display = self.motor_result_display
            status_label = self.motor_status_label
        elif 'camera' in method_name or 'download_file' in method_name:
            # 处理相机相关API，包括下载文件
            result_display = self.camera_result_display
            status_label = self.camera_status_label
        elif 'led' in method_name:
            result_display = self.led_result_display
            status_label = self.led_status_label
        elif 'lidar' in method_name:
            result_display = self.lidar_result_display
            status_label = self.lidar_status_label
        elif 'inclinometer' in method_name:
            result_display = self.inclinometer_result_display
            status_label = self.inclinometer_status_label
        elif 'system' in method_name or 'battery' in method_name or 'tf_card' in method_name:
            result_display = self.system_result_display
            status_label = self.system_status_label
        
        # 显示结果
        if result_display:
            success = result.get("success", False)
            message = result.get("message", "未知消息")
            result_display.append_result(f"{display_name}: {message}", success)
            
            # 显示详细数据
            if "data" in result:
                data_str = json.dumps(result["data"], ensure_ascii=False, indent=2)
                result_display.append_result(f"详细数据:\n{data_str}")
        
        # 更新状态标签
        if status_label:
            success = result.get("success", False)
            status_text = "成功" if success else "失败"
            status_label.set_status(f"{display_name}: {status_text}", success)
    
    def _disable_related_buttons(self, api_method, display_name):
        """禁用相关的按钮"""
        method_name = api_method.__name__
        
        # 定义按钮分组映射
        button_groups = {
            # 电源管理相关按钮
            'power_on': ['power_on_btn', 'power_off_btn'],
            'power_off': ['power_on_btn', 'power_off_btn'],
            'get_power_status': ['power_status_btn'],
            'power_on_all': ['power_on_all_btn', 'power_off_all_btn'],
            'power_off_all': ['power_on_all_btn', 'power_off_all_btn'],
            'get_devices_status': ['power_all_status_btn'],
            
            # 配置管理相关按钮
            'wifi_setup': ['wifi_setup_btn'],
            'sync_system_time': ['time_sync_btn'],
            'motor_configure': ['motor_config_btn'],
            'min_motor_configure': ['min_motor_config_btn'],
            'lidar_setup': ['lidar_config_btn'],
            'setup_all_devices': ['all_devices_setup_btn'],
            
            # 电机控制相关按钮
            'motor_find_zero': ['find_zero_btn'],
            'motor_get_angle': ['get_angle_btn'],
            'motor_set_position': ['set_position_btn'],
            'motor_set_speed': ['set_speed_btn'],
            'min_motor_set_angle': ['set_absolute_pos_btn'],
            'min_motor_relative_move': ['relative_move_btn'],
            'min_motor_read_angle': ['read_angle_btn'],
            'min_motor_detect_limits': ['detect_limits_btn'],
            
            # 相机控制相关按钮
            'camera_set_resolution': ['set_resolution_btn'],
            'camera_capture': ['capture_btn'],
            'camera_set_and_capture': ['set_and_capture_btn'],
            'download_file': ['download_image_btn'],
            
            # LED控制相关按钮
            'led_set_color': ['set_led_color_btn'],
            'led_set_custom_color': ['set_custom_color_btn'],
            'led_turn_off': ['turn_off_led_btn'],
            
            # 雷达控制相关按钮
            'lidar_get_sn': ['lidar_sn_btn'],
            'lidar_get_calibration': ['lidar_calib_btn'],
            
            # 倾角仪控制相关按钮
            'inclinometer_read': ['inc_read_btn'],
            
            # 系统信息相关按钮
            'get_system_info': ['system_info_btn'],
            'get_system_metrics': ['system_metrics_btn'],
            'get_battery_status': ['battery_status_btn'],
            'get_tf_card_status': ['tf_card_btn']
        }
        
        # 获取需要禁用的按钮
        buttons_to_disable = button_groups.get(method_name, [])
        
        # 禁用按钮并记录
        for button_attr in buttons_to_disable:
            if hasattr(self, button_attr):
                button = getattr(self, button_attr)
                button.setEnabled(False)
                self.active_buttons[button_attr] = {
                    'button': button,
                    'display_name': display_name
                }
                self.logger.debug(f"禁用按钮: {button_attr} ({display_name})")
    
    def _enable_related_buttons(self, api_method):
        """启用相关的按钮"""
        method_name = api_method.__name__
        
        # 定义按钮分组映射
        button_groups = {
            'power_on': ['power_on_btn', 'power_off_btn'],
            'power_off': ['power_on_btn', 'power_off_btn'],
            'get_power_status': ['power_status_btn'],
            'power_on_all': ['power_on_all_btn', 'power_off_all_btn'],
            'power_off_all': ['power_on_all_btn', 'power_off_all_btn'],
            'get_devices_status': ['power_all_status_btn'],
            'wifi_setup': ['wifi_setup_btn'],
            'sync_system_time': ['time_sync_btn'],
            'motor_configure': ['motor_config_btn'],
            'min_motor_configure': ['min_motor_config_btn'],
            'lidar_setup': ['lidar_config_btn'],
            'setup_all_devices': ['all_devices_setup_btn'],
            'motor_find_zero': ['find_zero_btn'],
            'motor_get_angle': ['get_angle_btn'],
            'motor_set_position': ['set_position_btn'],
            'motor_set_speed': ['set_speed_btn'],
            'min_motor_set_angle': ['set_absolute_pos_btn'],
            'min_motor_relative_move': ['relative_move_btn'],
            'min_motor_read_angle': ['read_angle_btn'],
            'min_motor_detect_limits': ['detect_limits_btn'],
            'camera_set_resolution': ['set_resolution_btn'],
            'camera_capture': ['capture_btn'],
            'camera_set_and_capture': ['set_and_capture_btn'],
            'download_file': ['download_image_btn'],
            'led_set_color': ['set_led_color_btn'],
            'led_set_custom_color': ['set_custom_color_btn'],
            'led_turn_off': ['turn_off_led_btn'],
            'lidar_get_sn': ['lidar_sn_btn'],
            'lidar_get_calibration': ['lidar_calib_btn'],
            'inclinometer_read': ['inc_read_btn'],
            'get_system_info': ['system_info_btn'],
            'get_system_metrics': ['system_metrics_btn'],
            'get_battery_status': ['battery_status_btn'],
            'get_tf_card_status': ['tf_card_btn']
        }
        
        # 获取需要启用的按钮
        buttons_to_enable = button_groups.get(method_name, [])
        
        # 启用按钮并移除记录
        for button_attr in buttons_to_enable:
            if button_attr in self.active_buttons:
                button_info = self.active_buttons.pop(button_attr)
                button = button_info['button']
                button.setEnabled(True)
                display_name = button_info['display_name']
                self.logger.debug(f"启用按钮: {button_attr} ({display_name})")
    
    def _on_thread_finished(self, thread, api_method):
        """线程完成时的回调"""
        # 启用相关按钮
        self._enable_related_buttons(api_method)
        
        # 从线程列表中移除已完成的线程
        if thread in self.test_threads:
            self.test_threads.remove(thread)
        
        self.logger.debug(f"线程完成: {api_method.__name__}")
    
    def switch_module(self, module_name):
        """切换模块"""
        self.logger.info(f"切换到模块: {module_name}")
        # 这里可以根据需要实现模块切换逻辑
        tab_index_map = {
            "power": 0,  # “电源管理”标签页，索引0
            "config": 1,  # “配置管理”标签页，索引1
            "turret":2,  # “转台控制”标签页，索引2
            "mini_motor": 2,  # “转台控制”标签页，索引2
            "motor": 2,  # “电机控制”标签页，索引2
            "camera": 3,  # “相机控制”标签页，索引3
            "lidar": 4,  # “雷达控制”标签页，索引4
            "inclinometer": 5,  # “倾角仪控制”标签页，索引5
            "led": 6,  # “LED控制”标签页，索引6
            "system": 7  # “系统信息”标签页，索引7
        }

        # 获取目标标签页的索引
        target_index = tab_index_map.get(module_name)

        if target_index is not None:
            # 确保索引在有效范围内，然后切换标签页
            if 0 <= target_index < self.control_panel.count():
                self.control_panel.setCurrentIndex(target_index)
            else:
                self.logger.error(f"模块 '{module_name}' 映射的标签页索引 {target_index} 无效。")
        else:
            self.logger.warning(f"未找到模块 '{module_name}' 对应的标签页映射。")
    
    def refresh(self):
        """刷新页面"""
        self.logger.info("刷新单模块控制页面")
        # 清空结果显示
        displays = [
            self.power_result_display,self.config_result_display,  # <- 新增
            self.motor_result_display,
            self.camera_result_display, self.led_result_display,
            self.lidar_result_display, self.inclinometer_result_display,
            self.system_result_display
        ]
        for display in displays:
            display.clear()
        
        # 重置状态标签
        labels = [
            self.power_status_label,self.config_status_label,    # <- 新增
            self.motor_status_label,
            self.camera_status_label, self.led_status_label,
            self.lidar_status_label, self.inclinometer_status_label,
            self.system_status_label
        ]
        for label in labels:
            label.set_status("状态: 未知")
        
        # 清理完成的线程
        self.test_threads = [t for t in self.test_threads if t.isRunning()]