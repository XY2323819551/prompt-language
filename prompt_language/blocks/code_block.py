from dataclasses import dataclass
from typing import Optional, Any
import json
from .base_block import BaseBlock
from prompt_language.utils.model_factory import get_model_response


@dataclass
class CodeResult:
    """代码执行结果"""
    code: Optional[str]  # 生成的代码（自然语言模式下）
    result: Any         # 执行结果


class CodeBlock(BaseBlock):
    async def execute(self, statement, gv_pool, tool_pool) -> None:
        assign_method, res_name, statement = await self.statement_parser.parse(statement, gv_pool)
        code_result = await self._execute_code_block(statement)  # code_result.code先留着
        await self.save_result(res_name, code_result.result, assign_method)
    
    async def _execute_code_block(self, content: str) -> CodeResult:
        content = content.strip()
        
        # JSON 类型
        if content.startswith('```json'):
            json_str = content[7:].strip().strip('`')
            try:
                result = json.loads(json_str)
                return CodeResult(code=None, result=result)
            except json.JSONDecodeError as e:
                raise ValueError(f"JSON 解析错误: {str(e)}")
        
        # Python 代码类型
        elif content.startswith('```python'):
            python_code = content[10:].strip().strip('`')
            try:
                # 创建局部变量空间
                local_vars = {}
                # 执行代码
                exec(python_code, {}, local_vars)
                # 获取结果（如果有）
                result = local_vars.get('result', None)
                return CodeResult(code=None, result=result)
            except Exception as e:
                raise ValueError(f"Python 代码执行错误: {str(e)}")
        
        # 自然语言类型
        else:
            # 调用大模型生成代码
            messages = [
                {
                    "role": "system",
                    "content": """你是一个 Python 代码生成器。
请根据用户的自然语言描述生成可执行的 Python 代码。

要求：
1. 生成的代码必须完整且可执行
2. 使用 result 变量存储最终结果
3. 代码应该简洁明了
4. 不要包含任何注释或说明
5. 只返回代码，不要有其他内容"""
                },
                {
                    "role": "user",
                    "content": f"请生成代码实现以下功能：{content}"
                }
            ]
            
            generated_code = await get_model_response(
                messages=messages,
                temperature=0
            )
            
            # 执行生成的代码
            try:
                local_vars = {}
                exec(generated_code, {}, local_vars)
                result = local_vars.get('result', None)
                return CodeResult(code=generated_code, result=result)
            except Exception as e:
                raise ValueError(f"生成的代码执行错误: {str(e)}")




