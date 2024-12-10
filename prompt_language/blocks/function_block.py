from dataclasses import dataclass
from typing import List, Dict, Any
from .base_block import BaseBlock
from prompt_language.utils.prompt_logger import logger


@dataclass
class FunctionCall:
    """函数调用的解析结果"""
    name: str           # 函数名
    args: List[str]     # 位置参数列表
    kwargs: Dict[str, str]  # 关键字参数字典


class FunctionBlock(BaseBlock):
    async def execute(self, statement, gv_pool, tool_pool) -> None:
        logger.info(f"执行函数: {statement}")
        
        parser_res = await self.statement_parser.parse(statement, gv_pool)
        assign_method, res_name, statement = parser_res.assign_method, parser_res.res_name, parser_res.statement
        
        function_call = await self._parse_function_call(statement)
        logger.debug(f"函数调用: {function_call}")
        
        result = await self._execute_function(function_call, tool_pool)
        logger.debug(f"函数返回: {result}")
        
        await self.save_result(res_name, result, assign_method, gv_pool)
        logger.info(f"变量赋值: {res_name} = {result}")

    
    async def _execute_function(self, function_call: FunctionCall, tool_pool: Any) -> Any:
        func = await tool_pool.get_tool(function_call.name)
        if not func:
            raise ValueError(f"未找到函数: {function_call.name}")
        
        try:
            if function_call.kwargs:
                result = await func(*function_call.args, **function_call.kwargs)
            else:
                result = await func(*function_call.args)
            return result
        except Exception as e:
            raise ValueError(f"函数执行失败: {str(e)}")
    
    async def _parse_function_call(self, statement: str) -> FunctionCall:
        """
        解析函数调用语句
        
        Args:
            statement: 形如 @get_weather("Shanghai") 或 
                      @get_data("weather", query="Shanghai") 的语句
            
        Returns:
            FunctionCall: 包含函数名和参数的数据类
            
        Examples:
            >>> _parse_function_call('@get_weather("Shanghai")')
            FunctionCall(name='get_weather', args=['Shanghai'], kwargs={})
            
            >>> _parse_function_call('@get_data("weather", query="Shanghai")')
            FunctionCall(name='get_data', args=['weather'], kwargs={'query': 'Shanghai'})
        """
        # 去除前后空格
        content = statement.strip()
        
        # 提取函数名（@后括号前的部分）
        if not content.startswith('@') or '(' not in content or not content.endswith(')'):
            raise ValueError(f"无效的函数调用语句: {content}")
            
        func_start = content.find('@') + 1
        func_end = content.find('(')
        func_name = content[func_start:func_end].strip()
        
        # 提取参数字符串（括号内的部分）
        params_str = content[func_end + 1:-1].strip()
        
        # 如果没有参数，直接返回
        if not params_str:
            return FunctionCall(name=func_name, args=[], kwargs={})
            
        # 解析参数
        args = []
        kwargs = {}
        
        # 分割参数
        params = []
        current_param = []
        in_quotes = False
        quote_char = None
        
        for char in params_str:
            if char in ['"', "'"]:
                if not in_quotes:
                    in_quotes = True
                    quote_char = char
                elif char == quote_char:
                    in_quotes = False
                current_param.append(char)
            elif char == ',' and not in_quotes:
                params.append(''.join(current_param).strip())
                current_param = []
            else:
                current_param.append(char)
                
        if current_param:
            params.append(''.join(current_param).strip())
        
        # 处理每个参数
        for param in params:
            param = param.strip()
            if '=' in param:  # 关键字参数
                key, value = param.split('=', 1)
                key = key.strip()
                value = value.strip()
                # 处理带引号的值
                if (value.startswith('"') and value.endswith('"')) or \
                   (value.startswith("'") and value.endswith("'")):
                    value = value[1:-1]
                kwargs[key] = value
            else:  # 位置参数
                # 处理带引号的值
                if (param.startswith('"') and param.endswith('"')) or \
                   (param.startswith("'") and param.endswith("'")):
                    param = param[1:-1]
                args.append(param)
        
        return FunctionCall(name=func_name, args=args, kwargs=kwargs)

