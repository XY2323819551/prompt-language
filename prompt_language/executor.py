from typing import Dict, Any, Optional
from prompt_language.config import GlobalVariablePool, GlobalToolPool
from prompt_language.parser.global_parser import GlobalParser
from prompt_language.parser.local_parser import LoopParser, JudgmentParser
from prompt_language.blocks.block_router import BlockRouter

class Executor: 
    def __init__(self):
        self.gv_pool = GlobalVariablePool()
        self.tool_pool = GlobalToolPool()
        self.parser = GlobalParser()
        self.loop_parser = LoopParser()
        self.judgment_parser = JudgmentParser()
        self.block_router = BlockRouter()
    
    async def init_execute(self, variables: Optional[Dict[str, Any]] = None, tools: Optional[Dict[str, Any]] = None) -> None:
        if variables:
            await self.gv_pool.init_variables(variables)
        if tools:
            await self.tool_pool.init_tools(tools)
    
    async def execute(self, statements: str) -> None:
        block_queue = await self.parser.parse(statements)
        while not block_queue.empty():
            block = await block_queue.get()
            if block.block_type == "loop":
                loop_parser_result = await self.loop_parser.parse(block.statements, self.gv_pool)
                for item in loop_parser_result.iteration_target:
                    self.gv_pool.set_variable(loop_parser_result.variable, item)
                    await self.execute(loop_parser_result.statement, self.gv_pool)
            elif block.block_type == "judgment":
                judgment_parser_result = await self.judgment_parser.parse(block.statements, self.gv_pool)
                await self.execute(judgment_parser_result.statement, self.gv_pool)
            else:  # code、condition_judge、exit、agent、function
                await self.block_router.execute_block(block.block_type, block.statements, self.gv_pool, self.tool_pool)
            
