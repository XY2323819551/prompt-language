from .base_block import BaseBlock

class AgentBlock(BaseBlock):
    async def execute(self, statement, gv_pool, tool_pool) -> None:
        assign_method, res_name, statement = await self.statement_parser.parse(statement, gv_pool)
        
        agent_type, task, tools = self._parse_agent_params(statement)
        result_key = self._get_result_key(statement)
        append_mode = self._is_append_mode(statement)
        
        agent = await self._create_agent(agent_type, task, tools)
        result = await agent.run()
        await self.save_result(res_name, result, assign_method) 
