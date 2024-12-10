from .base_block import BaseBlock
from prompt_language.utils.prompt_logger import logger


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
        logger.info(f"执行退出: {statement}")
        
        parser_res = await self.statement_parser.parse(statement, gv_pool)
        _, _, statement = parser_res.assign_method, parser_res.res_name, parser_res.statement
        
        msg = await self._parse_exit_message(statement)
        logger.debug(f"退出消息: {msg}")
        
        logger.info("程序退出")
        raise SystemExit(msg)
