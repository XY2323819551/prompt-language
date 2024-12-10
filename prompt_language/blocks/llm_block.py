from .base_block import BaseBlock
from prompt_language.utils.func_to_schema import function_to_schema
from prompt_language.utils.model_factory import get_model_response


class LLMBlock(BaseBlock):
    async def execute(self, statement, gv_pool, tool_pool) -> None:
        assign_method, res_name, statement = await self.statement_parser.parse(statement, gv_pool)
        result = await self._call_llm(statement, tool_pool)
        await self.save_result(res_name, result, assign_method)

    async def _call_llm(self, statement, tool_pool) -> str:
        """
        调用LLM并处理工具调用
        
        Args:
            statement: 用户输入的语句
            tool_pool: 工具池实例
            
        Returns:
            str: LLM的最终响应
        """
        tools_list = await tool_pool.get_all_tools()
        tool_schemas = [function_to_schema(tool) for tool in tools_list]
        messages = [{"role": "system", "content": statement}]
        
        response = await get_model_response(
            messages=messages,
            tools=tool_schemas if tool_schemas else None,
            temperature=0
        )
        
        message = response.choices[0].message
        messages.append(message)
        
        # 如果没有工具调用，返回内容
        if not message.tool_calls:
            return message.content
            
        # 处理工具调用
        for tool_call in message.tool_calls:
            tool_name = tool_call.function.name
            tool = await tool_pool.get_tool(tool_name)
            if not tool:
                return None
            result = await tool(**tool_call.function.arguments)
            return result
