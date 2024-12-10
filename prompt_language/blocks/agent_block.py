from .base_block import BaseBlock
from prompt_language.utils.prompt_logger import logger


class AgentBlock(BaseBlock):
    async def execute(self, statement, gv_pool, tool_pool) -> None:
        logger.info(f"执行Agent: {statement}")
        
        parser_res = await self.statement_parser.parse(statement, gv_pool)
        assign_method, res_name, statement = parser_res.assign_method, parser_res.res_name, parser_res.statement
        
        agent_type, task, tools = self._parse_agent_params(statement)
        logger.debug(f"Agent参数: type={agent_type}, task={task}, tools={len(tools)}个")
        
        agent = await self._create_agent(agent_type, task, tools)
        logger.debug(f"创建Agent: {agent}")
        
        result = await agent.run()
        logger.debug(f"Agent执行结果: {result}")
        
        await self.save_result(res_name, result, assign_method, gv_pool)
        logger.info(f"变量赋值: {res_name} = {result}")

    # ... (其他方法保持不变)
