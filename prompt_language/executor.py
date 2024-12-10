from typing import Dict, Any, Optional
from .config import GlobalVariablePool, GlobalToolPool
from .parser.global_parser import GlobalParser
from .blocks.block_router import BlockRouter

class Executor: 
    def __init__(self):
        self.variable_pool = GlobalVariablePool()
        self.tool_pool = GlobalToolPool()
        self.parser = GlobalParser()
        self.block_router = BlockRouter()
    
    async def init_execute(self, 
                          variables: Optional[Dict[str, Any]] = None,
                          tools: Optional[Dict[str, Any]] = None) -> None:
        if variables:
            await self.variable_pool.update_variables(variables)
        
        if tools:
            await self.tool_pool.register_tools(tools)
    
    async def execute(self, statements: str) -> None:
        block_queue = await self.parser.parse(statements)
        
        while not block_queue.empty():
            block = await block_queue.get()
            if block.block_type == "loop":
                # 对for语句进行解析
                pass
            elif block.block_type == "judgment":
                # 对if语句进行解析
                pass
            else:  # code、condition_judge、exit、agent、function
                await self.block_router.execute_block(block.block_type, block.statements)
            
