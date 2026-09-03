from PyQt5.QtWidgets import (
    QWidget, QGroupBox, QVBoxLayout, QHBoxLayout, QPushButton,
    QLabel, QComboBox, QLineEdit, QSpinBox, QDoubleSpinBox,
    QTextEdit, QProgressBar, QCheckBox, QListWidget, QTableWidget,
    QTableWidgetItem, QHeaderView, QFrame
)
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QFont


class ModuleGroupBox(QGroupBox):
    """模块分组框组件"""
    
    def __init__(self, title: str, parent=None):
        super().__init__(title, parent)
        self.setTitle(title)
        self.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                border: 2px solid gray;
                border-radius: 5px;
                margin-top: 1ex;
                padding-top: 10px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px 0 5px;
            }
        """)


class StatusLabel(QLabel):
    """状态标签组件"""
    
    def __init__(self, text: str = "", parent=None):
        super().__init__(text, parent)
        self.setAlignment(Qt.AlignCenter)
        self.setMinimumHeight(30)
        self.setStyleSheet("""
            QLabel {
                border: 1px solid gray;
                border-radius: 3px;
                padding: 5px;
                background-color: lightgray;
            }
        """)
    
    def set_status(self, status: str, success: bool = None):
        """设置状态"""
        self.setText(status)
        if success is True:
            self.setStyleSheet("""
                QLabel {
                    border: 1px solid green;
                    border-radius: 3px;
                    padding: 5px;
                    background-color: lightgreen;
                    color: darkgreen;
                }
            """)
        elif success is False:
            self.setStyleSheet("""
                QLabel {
                    border: 1px solid red;
                    border-radius: 3px;
                    padding: 5px;
                    background-color: lightcoral;
                    color: darkred;
                }
            """)
        else:
            self.setStyleSheet("""
                QLabel {
                    border: 1px solid gray;
                    border-radius: 3px;
                    padding: 5px;
                    background-color: lightgray;
                }
            """)


class ControlButton(QPushButton):
    """控制按钮组件"""
    
    def __init__(self, text: str, parent=None):
        super().__init__(text, parent)
        self.setMinimumHeight(35)
        self.setStyleSheet("""
            QPushButton {
                font-weight: bold;
                padding: 8px;
                border: 2px solid #2196F3;
                border-radius: 5px;
                background-color: #2196F3;
                color: white;
            }
            QPushButton:hover {
                background-color: #1976D2;
                border-color: #1976D2;
            }
            QPushButton:pressed {
                background-color: #0D47A1;
                border-color: #0D47A1;
            }
            QPushButton:disabled {
                background-color: #BDBDBD;
                border-color: #BDBDBD;
                color: #757575;
            }
        """)


class ResultDisplay(QTextEdit):
    """结果显示组件"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setReadOnly(True)
        self.setMaximumHeight(150)
        self.setFont(QFont("Consolas", 9))
        self.setStyleSheet("""
            QTextEdit {
                border: 1px solid #BDBDBD;
                border-radius: 3px;
                padding: 5px;
                background-color: #F5F5F5;
            }
        """)
    
    def append_result(self, text: str, success: bool = None):
        """追加结果显示"""
        if success is True:
            formatted_text = f"[✓ SUCCESS] {text}"
            color = "darkgreen"
        elif success is False:
            formatted_text = f"[✗ FAILED] {text}"
            color = "darkred"
        else:
            formatted_text = f"[INFO] {text}"
            color = "black"
        
        self.append(f'<span style="color: {color};">{formatted_text}</span>')


class TestProgressWidget(QWidget):
    """测试进度组件"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()
    
    def setup_ui(self):
        layout = QVBoxLayout(self)
        
        # 标题
        self.title_label = QLabel("测试进度")
        self.title_label.setStyleSheet("font-weight: bold; font-size: 14px;")
        layout.addWidget(self.title_label)
        
        # 进度条
        self.progress_bar = QProgressBar()
        self.progress_bar.setTextVisible(True)
        layout.addWidget(self.progress_bar)
        
        # 状态标签
        self.status_label = StatusLabel()
        layout.addWidget(self.status_label)
    
    def set_progress(self, value: int, max_value: int = 100):
        """设置进度"""
        self.progress_bar.setMaximum(max_value)
        self.progress_bar.setValue(value)
    
    def set_status(self, status: str, success: bool = None):
        """设置状态"""
        self.status_label.set_status(status, success)


class ModuleSelector(QWidget):
    """模块选择组件"""
    
    selection_changed = pyqtSignal(list)  # 选择改变信号
    
    def __init__(self, modules_config: dict, parent=None):
        super().__init__(parent)
        self.modules_config = modules_config
        self.checkboxes = {}
        self.setup_ui()
    
    def setup_ui(self):
        layout = QVBoxLayout(self)
        
        # 标题
        title = QLabel("选择测试模块:")
        title.setStyleSheet("font-weight: bold;")
        layout.addWidget(title)
        
        # 模块复选框
        for module_name, config in self.modules_config.items():
            checkbox = QCheckBox(config.get("name", module_name))
            checkbox.setChecked(True)
            checkbox.stateChanged.connect(self.on_selection_changed)
            self.checkboxes[module_name] = checkbox
            layout.addWidget(checkbox)
        
        # 全选/取消全选按钮
        button_layout = QHBoxLayout()
        select_all_btn = ControlButton("全选")
        select_all_btn.clicked.connect(self.select_all)
        button_layout.addWidget(select_all_btn)
        
        deselect_all_btn = ControlButton("取消全选")
        deselect_all_btn.clicked.connect(self.deselect_all)
        button_layout.addWidget(deselect_all_btn)
        
        layout.addLayout(button_layout)
    
    def on_selection_changed(self):
        """选择改变时发出信号"""
        selected_modules = self.get_selected_modules()
        self.selection_changed.emit(selected_modules)
    
    def get_selected_modules(self) -> list:
        """获取选中的模块列表"""
        return [name for name, checkbox in self.checkboxes.items() 
                if checkbox.isChecked()]
    
    def select_all(self):
        """全选所有模块"""
        for checkbox in self.checkboxes.values():
            checkbox.setChecked(True)
    
    def deselect_all(self):
        """取消全选所有模块"""
        for checkbox in self.checkboxes.values():
            checkbox.setChecked(False)


class ParameterInput(QWidget):
    """参数输入组件"""
    
    def __init__(self, param_name: str, param_type: str = "text", parent=None):
        super().__init__(parent)
        self.param_name = param_name
        self.param_type = param_type
        self.setup_ui()
    
    def setup_ui(self):
        layout = QHBoxLayout(self)
        
        # 参数标签
        label = QLabel(f"{self.param_name}:")
        label.setMinimumWidth(100)
        layout.addWidget(label)
        
        # 根据参数类型创建输入控件
        if self.param_type == "text":
            self.input_widget = QLineEdit()
        elif self.param_type == "number":
            self.input_widget = QSpinBox()
            self.input_widget.setRange(-999999, 999999)
        elif self.param_type == "decimal":
            self.input_widget = QDoubleSpinBox()
            self.input_widget.setRange(-999999.99, 999999.99)
            self.input_widget.setDecimals(2)
        elif self.param_type == "combo":
            self.input_widget = QComboBox()
        else:
            self.input_widget = QLineEdit()
        
        layout.addWidget(self.input_widget)
    
    def get_value(self):
        """获取输入值"""
        if isinstance(self.input_widget, QLineEdit):
            return self.input_widget.text()
        elif isinstance(self.input_widget, (QSpinBox, QDoubleSpinBox)):
            return self.input_widget.value()
        elif isinstance(self.input_widget, QComboBox):
            return self.input_widget.currentText()
        else:
            return self.input_widget.text()
    
    def set_value(self, value):
        """设置输入值"""
        if isinstance(self.input_widget, QLineEdit):
            self.input_widget.setText(str(value))
        elif isinstance(self.input_widget, QSpinBox):
            self.input_widget.setValue(int(float(value)))
        elif isinstance(self.input_widget, QDoubleSpinBox):
            self.input_widget.setValue(float(value))
        elif isinstance(self.input_widget, QComboBox):
            index = self.input_widget.findText(str(value))
            if index >= 0:
                self.input_widget.setCurrentIndex(index)