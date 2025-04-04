from abc import ABC, abstractmethod
from typing import Any, Dict, Optional
from prompt_language.parser.local_parser import StatementParser

class BaseBlock(ABC):
    def __init__(self):
        """初始化基类，创建 StatementParser 实例"""
        self.statement_parser = StatementParser()
    
    @abstractmethod
    async def execute(self, statement: str) -> None:
        """执行具体的block逻辑"""
        pass
    
    async def save_result(self, key, value, assign_method, gv_pool) -> None:
        """保存结果到变量池"""
        if assign_method in [">>"]:
            await gv_pool.append_variable(key, value)
        elif assign_method in ["->"]:
            await gv_pool.set_variable(key, value) 
