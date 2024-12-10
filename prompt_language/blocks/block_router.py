from typing import Optional
from .code_block import CodeBlock
from .condition_judge_block import ConditionJudgeBlock
from .exit_block import ExitBlock
from .agent_block import AgentBlock
from .function_block import FunctionBlock
from .llm_block import LLMBlock

class BlockRouter:
    def __init__(self):
        self.blocks = {
            "code": CodeBlock(),
            "condition_judge": ConditionJudgeBlock(),
            "exit": ExitBlock(),
            "agent": AgentBlock(),
            "function": FunctionBlock(),
            "llm": LLMBlock()
        }
    
    async def execute_block(self, block_type: str, statements: str):
        await self.blocks.get(block_type).execute(statements) 