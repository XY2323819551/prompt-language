import ast, json
from dataclasses import dataclass
from typing import List, Dict, Any
from .base_block import BaseBlock
from prompt_language.utils.prompt_logger import logger


@dataclass
class FunctionCall:
    """函数调用的解析结果"""
    name: str           # 函数名
    pos_args: List[str]     # 位置参数列表
    kwargs: Dict[str, str]  # 关键字参数字典


class FunctionBlock(BaseBlock):
    async def execute(self, statement, gv_pool, tool_pool) -> None:
        logger.info(f"执行函数: {statement}")
        parser_res = await self.statement_parser.parse(statement, gv_pool, retail_statement=True)
        assign_method, res_name, statement = parser_res.assign_method, parser_res.res_name, parser_res.statement
        
        function_call = await self._parse_function_call(statement, gv_pool)
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
                result = await func(*function_call.pos_args, **function_call.kwargs)
            else:
                result = await func(*function_call.pos_args)
            return result
        except Exception as e:
            raise ValueError(f"函数执行失败: {str(e)}")
        
    async def _get_variable_value(self, var_expr: str, gv_pool: Any) -> Any:
        """
        从变量池中获取变量值
        支持普通变量、列表索引和字典键值的获取
        """
        # 移除$符号
        if var_expr.startswith('$'):
            var_expr = var_expr[1:]
        
        # 处理复杂表达式 ${var.key} 或 ${var[index]}
        if var_expr.startswith('{') and var_expr.endswith('}'):
            var_expr = var_expr[1:-1]
            
            # 分离基础变量名和访问表达式
            parts = var_expr.split('.')
            base_var = parts[0]
            
            # 获取基础变量值
            value = await gv_pool.get_variable(base_var)
            if value is None:
                return var_expr
            
            # 处理后续的键值和索引访问
            for part in parts[1:]:
                # 检查是否包含列表索引
                if '[' in part and ']' in part:
                    key = part[:part.find('[')]
                    index_str = part[part.find('[')+1:part.find(']')]
                    try:
                        index = int(index_str)
                        value = value[key][index] if key else value[index]
                    except:
                        return var_expr
                else:
                    # 普通字典键值访问
                    try:
                        value = value[part]
                    except:
                        return var_expr
                    
            return value
        
        # 处理简单的列表索引 ${var[0]}
        if '[' in var_expr and ']' in var_expr:
            base_var = var_expr[:var_expr.find('[')]
            index_str = var_expr[var_expr.find('[')+1:var_expr.find(']')]
            
            value = await gv_pool.get_variable(base_var)
            if value is None:
                return var_expr
            
            try:
                index = int(index_str)
                return value[index]
            except:
                return var_expr
        
        # 普通变量
        value = await gv_pool.get_variable(var_expr)
        return value if value is not None else var_expr

    async def _parse_function_call(self, statement: str, gv_pool: Any) -> FunctionCall:
        """
        解析函数调用语句
        
        pos_args:
            statement: 函数调用语句，如 @get_weather("Shanghai") 或 @get_data($weather, query=$query)
            
        Returns:
            FunctionCall: 包含函数名和参数的数据类
        """
        # 1. 提取函数名
        if not statement.startswith('@') or '(' not in statement or not statement.endswith(')'):
            raise ValueError(f"无效的函数调用语句: {statement}")
        
        func_name = statement[1:statement.find('(')].strip()
        
        # 2. 提取参数字符串
        params_str = statement[statement.find('(')+1:-1].strip()
        if not params_str:
            return FunctionCall(name=func_name, pos_args=[], kwargs={})
        
        # 3. 分割参数
        params = []
        current = []
        in_quotes = False
        quote_char = None
        
        for char in params_str:
            if char in ['"', "'"]:
                if not in_quotes:
                    in_quotes = True
                    quote_char = char
                elif char == quote_char:
                    in_quotes = False
                current.append(char)
            elif char == ',' and not in_quotes:
                params.append(''.join(current).strip())
                current = []
            else:
                current.append(char)
        
        if current:
            params.append(''.join(current).strip())
        
        # 4. 解析参数
        pos_args = []
        kwargs = {}
        
        for param in params:
            param = param.strip()
            if '=' in param:  # 关键字参数
                key, value = param.split('=', 1)
                key = key.strip()
                value = value.strip()
                
                # 处理引号
                if (value.startswith('"') and value.endswith('"')) or \
                   (value.startswith("'") and value.endswith("'")):
                    value = value[1:-1]
                    
                kwargs[key] = value
            else:  # 位置参数
                # 处理引号
                if (param.startswith('"') and param.endswith('"')) or \
                   (param.startswith("'") and param.endswith("'")):
                    param = param[1:-1]
                    
                pos_args.append(param)

        # 处理位置参数中的变量引用
        processed_args = []
        for arg in pos_args:
            if isinstance(arg, str) and ('$' in arg):
                value = await self._get_variable_value(arg, gv_pool)
                processed_args.append(value)
            else:
                processed_args.append(arg)
        
        # 处理关键字参数中的变量引用
        processed_kwargs = {}
        for key, value in kwargs.items():
            if isinstance(value, str) and ('$' in value):
                processed_value = await self._get_variable_value(value, gv_pool)
                processed_kwargs[key] = processed_value
            else:
                processed_kwargs[key] = value
        return FunctionCall(name=func_name, pos_args=processed_args, kwargs=processed_kwargs)

