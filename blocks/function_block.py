from .base_block import BaseBlock
from typing import Any, Dict

class FunctionBlock(BaseBlock):
    async def execute(self, statement: str) -> None:
        """
        执行函数调用并将结果存入变量池
        """
        func_name, args, kwargs = self._parse_function_call(statement)
        result_key = self._get_result_key(statement)
        append_mode = self._is_append_mode(statement)
        
        result = await self._execute_function(func_name, args, kwargs)
        await self.save_result(result_key, result, append_mode) 