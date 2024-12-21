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
        """从变量池中获取变量值"""
        if not isinstance(var_expr, str):
            return var_expr
        
        result = var_expr
        pos = 0
        
        while True:
            # 1. 找到下一个$
            dollar_pos = result.find('$', pos)
            if dollar_pos == -1:
                break
            
            # 2. 确定变量范围
            if result[dollar_pos:].startswith('${'):
                end = result.find('}', dollar_pos)
                if end == -1:
                    pos = dollar_pos + 2
                    continue
                var_name = result[dollar_pos+2:end]  # 去掉${}
                full_var = result[dollar_pos:end+1]
            else:
                end = dollar_pos + 1
                while end < len(result) and (result[end].isalnum() or result[end] == '_'):
                    end += 1
                var_name = result[dollar_pos+1:end]  # 去掉$
                full_var = result[dollar_pos:end]
            
            # 3. 获取基础变量
            base_var = var_name.split('.')[0].split('[')[0]
            value = await gv_pool.get_variable(base_var)
            
            if value is None:
                pos = end
                continue
            
            # 4. 处理后续访问
            if '.' in var_name:
                try:
                    for part in var_name.split('.')[1:]:
                        value = value[part]
                except:
                    pos = end
                    continue
                
            if '[' in var_name:
                try:
                    index = int(var_name[var_name.find('[')+1:var_name.find(']')])
                    value = value[index]
                except:
                    pos = end
                    continue
                
            # 5. 替换变量
            result = result[:dollar_pos] + str(value) + result[end+1:]
            pos = dollar_pos + len(str(value))
        
        return result

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

        # 处理位置参数的变量引用
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


if __name__ == "__main__":
    import asyncio
    from dataclasses import dataclass
    
    @dataclass
    class MockGlobalVariablePool:
        def __init__(self):
            self.variables = {
                "paper_summary": ["摘要1", "摘要2", "摘要3"],
                "paper": {
                    "title": "测试论文",
                    "abstract": "这是摘要",
                    "authors": ["作者1", "作者2"],
                    "date": "2024-03-20"
                },
                "results": {
                    "data": {"title": "标题1", "content": "内容1"}
                }
            }
        
        async def get_variable(self, name: str):
            return self.variables.get(name)
    
    async def test_variable_value():
        gv_pool = MockGlobalVariablePool()
        block = FunctionBlock()
        
        test_cases = [
            # 列表索引访问
            "${paper_summary[-1]}",  # 应返回 "摘要3"
            "${paper_summary[0]}",   # 应返回 "摘要1"
            
            # 字典键值访问
            "${paper.title}",        # 应返回 "测试论文"
            "${paper.abstract}",     # 应返回 "这是摘要"
            
            # 字符串拼接
            "papers/${paper.title}.md",  # 应返回 "papers/测试论文.md"
            "output/${results.data.title}/data",  # 应返回 "output/标题1/data"
            
            # 多变量替换
            "${paper.title}_${paper.date}"  # 应返回 "测试论文_2024-03-20"
        ]
        
        for case in test_cases:
            result = await block._get_variable_value(case, gv_pool)
            print(f"\n测试用例: {case}")
            print(f"返回结果: {result}")
    
    asyncio.run(test_variable_value())

