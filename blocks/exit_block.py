from .base_block import BaseBlock
from typing import Any

class ExitBlock(BaseBlock):
    async def execute(self, statement: str) -> None:
        """
        执行退出操作
        """
        msg = self._parse_exit_message(statement)
        raise SystemExit(msg) 