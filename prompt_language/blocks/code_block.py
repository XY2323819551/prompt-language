from .base_block import BaseBlock


class CodeBlock(BaseBlock):
    async def execute(self, statement, gv_pool, tool_pool) -> None:
        assign_method, res_name, statement = await self.statement_parser.parse(statement, gv_pool)
        
        code_content = self._parse_code_content(statement)
        result_key = self._get_result_key(statement)
        append_mode = self._is_append_mode(statement)
        
        if self._is_python_code(code_content):
            result = await self._execute_python(code_content)
        elif self._is_json_data(code_content):
            result = await self._execute_json(code_content)
        else:
            result = await self._execute_natural_language(code_content)
            
        await self.save_result(res_name, result, assign_method)

