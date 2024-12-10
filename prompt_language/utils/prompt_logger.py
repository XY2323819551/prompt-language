import logging
import sys
from datetime import datetime
from typing import Any
from pathlib import Path
import inspect


class PromptLogger:
    """提示词日志记录器"""
    
    def __init__(self, log_level: str = "INFO"):
        """
        初始化日志记录器
        
        Args:
            log_level: 日志级别，可选值：
                - "DEBUG": 显示所有日志
                - "INFO": 显示一般信息（默认）
                - "ERROR": 只显示错误信息
        """
        # 配置日志格式
        self.logger = logging.getLogger("PromptLogger")
        
        # 防止日志重复
        self.logger.propagate = False
        
        # 确保处理器不会重复添加
        if self.logger.handlers:
            self.logger.handlers.clear()
        
        # 设置日志级别
        level_map = {
            "DEBUG": logging.DEBUG,
            "INFO": logging.INFO,
            "ERROR": logging.ERROR
        }
        self.logger.setLevel(level_map.get(log_level, logging.INFO))
        
        # 添加控制台处理器
        handler = logging.StreamHandler(sys.stdout)
        handler.setLevel(self.logger.level)
        
        # 设置颜色格式
        handler.setFormatter(ColoredFormatter())
        self.logger.addHandler(handler)
    
    def _get_caller_info(self) -> str:
        """获取调用者信息"""
        frame = inspect.currentframe()
        caller = inspect.getouterframes(frame)[2]
        
        filename = Path(caller.filename).name
        lineno = caller.lineno
        func = caller.function
        
        return f"{filename}:{func}:{lineno}"
    
    def debug(self, message: Any) -> None:
        """调试信息"""
        caller_info = self._get_caller_info()
        self.logger.debug(f"{caller_info} - {message}")
    
    def info(self, message: Any) -> None:
        """一般信息"""
        caller_info = self._get_caller_info()
        self.logger.info(f"{caller_info} - {message}")
    
    def error(self, message: Any) -> None:
        """错误信息"""
        caller_info = self._get_caller_info()
        self.logger.error(f"{caller_info} - {message}")


class ColoredFormatter(logging.Formatter):
    """带颜色的日志格式化器"""
    
    COLORS = {
        'DEBUG': '\033[94m',    # 蓝色
        'INFO': '\033[92m',     # 绿色
        'ERROR': '\033[91m',    # 红色
        'RESET': '\033[0m'      # 重置
    }
    
    def format(self, record):
        # 添加时间戳
        time_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]
        
        # 添加颜色
        color = self.COLORS.get(record.levelname, '')
        reset = self.COLORS['RESET']
        
        # 格式化消息
        return f"{color}[{time_str}] {record.getMessage()}{reset}"


# 创建全局实例
logger = PromptLogger(log_level="INFO")
