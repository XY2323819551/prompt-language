import json
from .base_block import BaseBlock
from prompt_language.utils.func_to_schema import function_to_schema
from prompt_language.utils.model_factory import get_model_response
from prompt_language.utils.prompt_logger import logger


class LLMBlock(BaseBlock):
    async def execute(self, statement, gv_pool, tool_pool) -> None:
        logger.info(f"执行LLM调用: {statement}")
        
        parser_res = await self.statement_parser.parse(statement, gv_pool)
        assign_method, res_name, statement = parser_res.assign_method, parser_res.res_name, parser_res.statement
        
        logger.debug(f"解析结果: {parser_res}")
        result = await self._call_llm(statement, tool_pool)
        logger.debug(f"LLM返回: {result}")
        
        await self.save_result(res_name, result, assign_method, gv_pool)
        logger.info(f"变量赋值: {res_name} = {result}")

    async def _call_llm(self, statement, tool_pool) -> str:
        tools_list = await tool_pool.get_all_tools()
        tool_schemas = [function_to_schema(tool) for tool in tools_list]
        messages = [{"role": "system", "content": statement}]
        
        response = await get_model_response(
            model_name="gpt-4o-mini",
            messages=messages,
            tools=tool_schemas if tool_schemas else None,
            temperature=0
        )
        message = response.choices[0].message
        
        # 如果没有工具调用，返回内容
        if not message.tool_calls:
            return message.content
            
        # 处理工具调用
        for tool_call in message.tool_calls:
            tool_name = tool_call.function.name
            
            tool = await tool_pool.get_tool(tool_name)
            arguments = json.loads(tool_call.function.arguments)
            
            if not tool:
                logger.error(f"工具不存在: {tool_name}")
                return None
                
            result = await tool(**arguments)
            return result
