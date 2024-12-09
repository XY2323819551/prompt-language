from .base_block import BaseBlock
from typing import Any, Dict, Optional

class AgentBlock(BaseBlock):
    async def execute(self, statement: str) -> None:
        """
        执行Agent调用并将结果存入变量池
        """
        agent_type, task, tools = self._parse_agent_params(statement)
        result_key = self._get_result_key(statement)
        append_mode = self._is_append_mode(statement)
        
        agent = await self._create_agent(agent_type, task, tools)
        result = await agent.run()
        await self.save_result(result_key, result, append_mode) 