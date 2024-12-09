from .base_block import BaseBlock
from typing import Any
import ast

class CodeBlock(BaseBlock):
    async def execute(self, statement: str) -> None:
        """
        执行代码块并将结果存入变量池
        """
        code_content = self._parse_code_content(statement)
        result_key = self._get_result_key(statement)
        append_mode = self._is_append_mode(statement)
        
        if self._is_python_code(code_content):
            result = await self._execute_python(code_content)
        elif self._is_json_data(code_content):
            result = await self._execute_json(code_content)
        else:
            result = await self._execute_natural_language(code_content)
            
        await self.save_result(result_key, result, append_mode)

