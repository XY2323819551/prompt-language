from .base_block import BaseBlock
from typing import Any

class LLMBlock(BaseBlock):
    async def execute(self, statement: str) -> None:
        """
        执行LLM调用并将结果存入变量池
        """
        prompt = self._parse_prompt(statement)
        result_key = self._get_result_key(statement)
        append_mode = self._is_append_mode(statement)
        
        result = await self._call_llm(prompt)
        await self.save_result(result_key, result, append_mode) 