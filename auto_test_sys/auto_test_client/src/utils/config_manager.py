import yaml
import os
from typing import Dict, Any


class ConfigManager:
    """配置管理器"""
    
    def __init__(self, config_path: str = None):
        # 如果没有指定配置路径，则自动寻找配置文件
        if config_path is None:
            self.config_path = self._find_config_file()
        else:
            self.config_path = config_path
        self.config = self.load_config()
    
    def _find_config_file(self) -> str:
        """自动寻找配置文件路径"""
        # 获取当前文件所在的目录
        current_dir = os.path.dirname(os.path.abspath(__file__))
        
        # 尝试不同的可能位置
        possible_paths = [
            # 1. 当前目录下的config.yaml
            os.path.join(current_dir, '..', '..', 'config.yaml'),
            # 2. 项目根目录下的config.yaml
            os.path.join(current_dir, '..', '..', '..', 'auto_test_client', 'config.yaml'),
            # 3. 工作目录下的config.yaml
            'config.yaml',
            # 4. 上一级目录的config.yaml
            os.path.join(current_dir, '..', 'config.yaml')
        ]
        
        for path in possible_paths:
            abs_path = os.path.abspath(path)
            if os.path.exists(abs_path):
                return abs_path
        
        # 如果都没找到，返回默认路径
        return os.path.abspath('config.yaml')
    
    def load_config(self) -> Dict[str, Any]:
        """加载配置文件"""
        print(f"正在加载配置文件: {self.config_path}")  # 调试信息
        if os.path.exists(self.config_path):
            with open(self.config_path, 'r', encoding='utf-8') as f:
                return yaml.safe_load(f)
        else:
            print(f"配置文件不存在: {self.config_path}，使用默认配置")
            # 返回默认配置
            return self.get_default_config()
    
    def get_default_config(self) -> Dict[str, Any]:
        """获取默认配置"""
        return {
            "server": {
                "host": "127.0.0.1",
                "port": 8000,
                "base_url": "http://127.0.0.1:8000/api/v1"
            },
            "modules": {
                "power": {
                    "name": "电源管理",
                    "enabled": True,
                    "modules": ["radar", "motor", "zt", "laser", "inc", "camera1", "camera2", "led"]
                },
                "motor": {
                    "name": "电机控制",
                    "enabled": True,
                    "types": ["转台电机", "小电机"]
                },
                "camera": {
                    "name": "相机控制",
                    "enabled": True,
                    "resolutions": ["12M", "16M", "8M", "4K", "1080p"]
                },
                "lidar": {
                    "name": "雷达控制",
                    "enabled": True
                },
                "led": {
                    "name": "LED控制",
                    "enabled": True,
                    "colors": ["green", "red", "white", "off"]
                }
            },
            "logging": {
                "level": "INFO",
                "file": "logs/client.log",
                "max_size": 10485760,
                "backup_count": 5
            }
        }
    
    def get(self, key: str, default=None):
        """获取配置项"""
        keys = key.split('.')
        value = self.config
        try:
            for k in keys:
                value = value[k]
            return value
        except (KeyError, TypeError):
            return default
    
    def get_server_url(self) -> str:
        """获取服务器URL"""
        return self.get("server.base_url", "http://127.0.0.1:8000/api/v1")
    
    def get_enabled_modules(self) -> Dict[str, Any]:
        """获取启用的模块配置"""
        modules = self.get("modules", {})
        return {name: config for name, config in modules.items() 
                if config.get("enabled", False)}