from .base_block import BaseBlock

class FunctionBlock(BaseBlock):
    async def execute(self, statement, gv_pool, tool_pool) -> None:
        assign_method, res_name, statement = await self.statement_parser.parse(statement, gv_pool)
        
        func_name, args, kwargs = self._parse_function_call(statement)
        result_key = self._get_result_key(statement)
        append_mode = self._is_append_mode(statement)
        
        result = await self._execute_function(func_name, args, kwargs)
        await self.save_result(res_name, result, assign_method)  