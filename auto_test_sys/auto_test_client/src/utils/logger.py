import logging
import os
from logging.handlers import RotatingFileHandler
from typing import Optional


class LoggerManager:
    """日志管理器"""
    
    def __init__(self, config_manager):
        self.config_manager = config_manager
        self.logger = self.setup_logger()
    
    def setup_logger(self) -> logging.Logger:
        """设置日志记录器"""
        # 创建logger
        logger = logging.getLogger('auto_test_client')
        logger.setLevel(getattr(logging, self.config_manager.get("logging.level", "INFO")))
        
        # 避免重复添加handler
        if logger.handlers:
            return logger
        
        # 创建格式器
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        
        # 控制台处理器
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)
        
        # 文件处理器
        log_file = self.config_manager.get("logging.file", "logs/client.log")
        log_dir = os.path.dirname(log_file)
        if log_dir and not os.path.exists(log_dir):
            os.makedirs(log_dir)
        
        max_size = self.config_manager.get("logging.max_size", 10485760)  # 10MB
        backup_count = self.config_manager.get("logging.backup_count", 5)
        
        file_handler = RotatingFileHandler(
            log_file, 
            maxBytes=max_size, 
            backupCount=backup_count,
            encoding='utf-8'
        )
        file_handler.setLevel(logging.DEBUG)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
        
        return logger
    
    def get_logger(self) -> logging.Logger:
        """获取logger实例"""
        return self.logger


# 全局logger实例
_logger_instance = None


def get_logger(config_manager=None) -> logging.Logger:
    """获取全局logger实例"""
    global _logger_instance
    if _logger_instance is None and config_manager is not None:
        _logger_instance = LoggerManager(config_manager).get_logger()
    return _logger_instance