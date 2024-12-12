from dataclasses import dataclass
from typing import Optional, Any
import json
from .base_block import BaseBlock
from prompt_language.utils.model_factory import get_model_response
from prompt_language.utils.prompt_logger import logger


@dataclass
class CodeResult:
    """代码执行结果"""
    code: Optional[str]  # 生成的代码（自然语言模式下）
    result: Any         # 执行结果


class CodeBlock(BaseBlock):
    async def execute(self, statement, gv_pool, tool_pool) -> None:
        logger.info(f"执行代码块: {statement}")
        
        parser_res = await self.statement_parser.parse(statement, gv_pool)
        assign_method, res_name, statement = parser_res.assign_method, parser_res.res_name, parser_res.statement

        logger.debug(f"解析结果: {parser_res}")
        code_result = await self._execute_code_block(statement)
        logger.debug(f"执行结果: {code_result}")
        
        await self.save_result(res_name, code_result.result, assign_method, gv_pool)
        logger.info(f"变量赋值: {res_name} = {code_result.result}")
    
    async def _execute_code_block(self, content: str) -> CodeResult:
        content = content.strip()
        
        # 提取 @code() 中的内容
        if not (content.startswith('@code(') and content.endswith(')')):
            raise ValueError(f"无效的代码块格式: {content}")
        
        # 提取括号内的内容
        code_content = content[6:-1].strip()  # 去掉 @code( 和 )
        
        # JSON 类型
        if code_content.startswith('```json'):
            json_str = code_content[7:].strip().strip('`')  # 去掉 ```json 和 结尾的 ```
            try:
                result = json.loads(json_str)
                return CodeResult(code=None, result=result)
            except json.JSONDecodeError as e:
                raise ValueError(f"JSON 解析错误: {str(e)}")
        
        # Python 代码类型
        elif code_content.startswith('```python'):
            python_code = code_content[10:].strip().strip('`').rstrip('\n')  # 去掉 ```python 和 结尾的 ```
            try:
                globals_dict = {'__builtins__': __builtins__}
                local_vars = {}
                exec(python_code, globals_dict, local_vars)
                last_assigned_var = None
                for var_name in local_vars:
                    if not var_name.startswith('__'):
                        last_assigned_var = local_vars[var_name]
                return CodeResult(code=None, result=last_assigned_var)
            except Exception as e:
                raise ValueError(f"Python 代码执行错误: {str(e)}")
        
        # 自然语言类型
        else:
            # 调用大模型生成代码
            messages = [
                {
                    "role": "user",
                    "content": f"""你是一个 Python 代码生成器。
请根据用户的自然语言描述生成可执行的 Python 代码。

要求：
1. 生成的代码必须完整且可执行
2. 只返回代码，不要有其他内容，代码使用标准的markdown格式返回

用户的自然语言描述如下：
{code_content}
"""
                },
            ]
            
            response = await get_model_response(
                messages=messages,
                temperature=0
            )
            
            # 从响应中提取代码
            generated_code = response.choices[0].message.content
            
            # 去除 markdown 格式
            if generated_code.startswith('```python\n'):
                generated_code = generated_code[10:]  # 去掉 ```python\n
            if generated_code.endswith('\n```'):
                generated_code = generated_code[:-4]  # 去掉 \n```
            
            # 执行生成的代码
            try:
                local_vars = {}
                exec(generated_code, {}, local_vars)
                result = local_vars.get('result', None)
                return CodeResult(code=generated_code, result=result)
            except Exception as e:
                raise ValueError(f"生成的代码执行错误: {str(e)}")




