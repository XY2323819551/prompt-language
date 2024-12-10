from .base_block import BaseBlock

class ExitBlock(BaseBlock):
    async def _parse_exit_message(self, statement: str) -> str:
        content = statement.strip()
        if not content.startswith('@exit(') or not content.endswith(')'):
            return ""
            
        params = content[6:-1].strip()
        if not params:
            return ""
            
        # 解析msg参数
        if params.startswith('msg='):
            msg = params[4:].strip()  # 去掉 msg=
            # 去掉引号（支持单引号和双引号）
            if (msg.startswith('"') and msg.endswith('"')) or \
               (msg.startswith("'") and msg.endswith("'")):
                msg = msg[1:-1]
            return msg
            
        return ""

    async def execute(self, statement, gv_pool, tool_pool) -> None:
        _, _, statement = await self.statement_parser.parse(statement, gv_pool)
        msg = await self._parse_exit_message(statement)
        raise SystemExit(msg)
