import logging
import sys
from datetime import datetime
from typing import Any
from pathlib import Path
import inspect
from enum import Enum


class BlockColor:
    """不同block类型对应的颜色"""
    CODE = '\033[38;5;214m'      # 橙色
    FUNCTION = '\033[38;5;45m'   # 蓝色
    LLM = '\033[38;5;135m'       # 紫色
    CONDITION = '\033[38;5;118m' # 绿色
    AGENT = '\033[38;5;203m'     # 红色
    EXIT = '\033[38;5;244m'      # 灰色
    LOOP = '\033[38;5;226m'      # 黄色
    JUDGMENT = '\033[38;5;51m'   # 青色
    ERROR = '\033[91m'           # 红色
    RESET = '\033[0m'            # 重置


class PromptLogger:
    """提示词日志记录器"""
    
    def __init__(self, log_level: str = "INFO"):
        """初始化日志记录器"""
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
        self.logger.addHandler(handler)
    
    def _get_caller_info(self) -> tuple[str, str]:
        """获取调用者信息"""
        frame = inspect.currentframe()
        caller = inspect.getouterframes(frame)[2]
        
        filename = Path(caller.filename).name
        block_type = filename.replace('_block.py', '').upper()
        
        return filename, block_type
    
    def _get_block_color(self, block_type: str) -> str:
        """获取block类型对应的颜色"""
        color_map = {
            'CODE': BlockColor.CODE,
            'FUNCTION': BlockColor.FUNCTION,
            'LLM': BlockColor.LLM,
            'CONDITION_JUDGE': BlockColor.CONDITION,
            'AGENT': BlockColor.AGENT,
            'EXIT': BlockColor.EXIT,
            'LOOP': BlockColor.LOOP,
            'JUDGMENT': BlockColor.JUDGMENT
        }
        return color_map.get(block_type, '')
    
    def _format_message(self, message: Any, block_type: str, filename: str) -> str:
        """格式化日志消息"""
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]
        color = self._get_block_color(block_type)
        return f"{color}[{now}] {block_type}:{filename} - {message}{BlockColor.RESET}"
    
    def debug(self, message: Any) -> None:
        """调试信息"""
        filename, block_type = self._get_caller_info()
        formatted_msg = self._format_message(message, block_type, filename)
        self.logger.debug(formatted_msg)
    
    def info(self, message: Any) -> None:
        """一般信息"""
        filename, block_type = self._get_caller_info()
        formatted_msg = self._format_message(message, block_type, filename)
        self.logger.info(formatted_msg)
    
    def error(self, message: Any) -> None:
        """错误信息"""
        filename, block_type = self._get_caller_info()
        formatted_msg = f"{BlockColor.ERROR}[ERROR] {block_type}:{filename} - {message}{BlockColor.RESET}"
        self.logger.error(formatted_msg)


# 创建全局实例
logger = PromptLogger(log_level="INFO")
