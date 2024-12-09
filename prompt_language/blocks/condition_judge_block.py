class ConditionJudgeBlock(BaseBlock):
    async def execute(self, statement: str) -> None:
        """
        执行条件判断并将结果存入变量池
        """
        variable, categories = self._parse_condition(statement)
        result_key = self._get_result_key(statement)
        append_mode = self._is_append_mode(statement)
        
        result = await self._classify_content(variable, categories)
        await self.save_result(result_key, result, append_mode) 