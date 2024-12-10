"""
函数到 JSON Schema 转换工具。

这个模块提供了将 Python 函数转换为 JSON Schema 的功能，主要用于：
1. 解析函数的签名和文档字符串
2. 生成符合 OpenAI Function Calling 格式的 JSON Schema
3. 支持类型注解和参数描述的提取

主要功能：
- function_to_schema: 将 Python 函数转换为 JSON Schema
- parse_docstring: 解析函数的 docstring，提取描述和参数信息

使用示例：
    >>> def greet(name: str, age: int = 0):
    ...     '''Say hello to someone.
    ...     
    ...     Args:
    ...         name (str): The person's name
    ...         age (int, optional): The person's age
    ...     '''
    ...     pass
    >>> schema = function_to_schema(greet)
    >>> print(schema['function']['name'])
    'greet'

注意事项：
- 函数必须有有效的类型注解
- docstring 必须遵循 Google 风格
- 支持可选参数和默认值
"""

import re
import json
import inspect
import requests 
from bs4 import BeautifulSoup

def parse_docstring(docstring):
    """
    解析函数的 docstring，提取函数描述和参数描述。

    Args:
        docstring (str): 函数的 docstring

    Returns:
        tuple: (函数描述, 参数描述的字典)
    """
    if not docstring:
        return "", {}

    # 分割 docstring
    parts = docstring.split("Args:")
    
    # 获取函数主描述
    main_description = parts[0].strip()
    
    # 解析参数描述
    param_descriptions = {}
    if len(parts) > 1:
        # 提取 Args 部分到下一个主要部分（Returns:, Raises:, Examples:, Note: 等）
        args_section = parts[1].split('\n\n')[0]
        # 解析每个参数
        param_patterns = re.finditer(r'(\w+)\s*\(([\w\s,]+)\):\s*([^\n]+)', args_section)
        for match in param_patterns:
            param_name = match.group(1)
            param_description = match.group(3).strip()
            param_descriptions[param_name] = param_description

    return main_description, param_descriptions

def function_to_schema(func) -> dict:
    """
    Converts a Python function into a JSON-serializable dictionary
    that describes the function's signature, including its name,
    description, and parameters.

    Args:
        func: The function to be converted.

    Returns:
        A dictionary representing the function's signature in JSON format.
    """
    type_map = {
        str: "string",
        int: "integer",
        float: "number",
        bool: "boolean",
        list: "array",
        dict: "object",
        type(None): "null",
    }

    try:
        signature = inspect.signature(func)
    except ValueError as e:
        raise ValueError(
            f"Failed to get signature for function {func.__name__}: {str(e)}"
        )

    # 解析 docstring
    main_description, param_descriptions = parse_docstring(func.__doc__)

    parameters = {}
    for param in signature.parameters.values():
        try:
            param_type = type_map.get(param.annotation, "string")
        except KeyError as e:
            raise KeyError(
                f"Unknown type annotation {param.annotation} for parameter {param.name}: {str(e)}"
            )
        
        param_info = {
            "type": param_type
        }
        
        # 添加参数描述（如果存在）
        if param.name in param_descriptions:
            param_info["description"] = param_descriptions[param.name]

        parameters[param.name] = param_info

    required = [
        param.name
        for param in signature.parameters.values()
        if param.default == inspect._empty
    ]

    return {
        "type": "function",
        "function": {
            "name": func.__name__,
            "description": main_description,
            "parameters": {
                "type": "object",
                "properties": parameters,
                "required": required,
            },
        },
    }

