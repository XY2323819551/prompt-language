from .base_block import BaseBlock

class ConditionJudgeBlock(BaseBlock):
    async def execute(self, statement, gv_pool, tool_pool) -> None:
        assign_method, res_name, statement = await self.statement_parser.parse(statement, gv_pool)
        
        variable, categories = self._parse_condition(statement)
        result_key = self._get_result_key(statement)
        append_mode = self._is_append_mode(statement)
        
        result = await self._classify_content(variable, categories)
        
        await self.save_result(res_name, result, assign_method) 

