import os
import json
import aiofiles
from typing import Union

async def read_local(filepath: str) -> Union[str, list, dict]:
    full_path = os.path.join("output", filepath)
    if not os.path.exists(full_path):
        raise FileNotFoundError(f"文件不存在: {full_path}")
    
    async with aiofiles.open(full_path, 'r', encoding='utf-8') as f:
        content = await f.read()
    
    _, ext = os.path.splitext(filepath)  # 根据文件扩展名处理内容
    
    if ext == '.json':
        try:
            return json.loads(content)
        except json.JSONDecodeError:
            return content
    
    return content.strip()

if __name__ == "__main__":
    import asyncio
    
    async def test():
        # 测试读取文本文件
        text_content = await read_local("books/test_str.txt")
        print("文本内容:", text_content)
        print("-" * 50)
        
        # 测试读取列表文件
        list_content = await read_local("books/test_list.json")
        print("列表内容:", list_content)
        print("类型:", type(list_content))
        print("-" * 50)
        
        # 测试读取字典文件
        dict_content = await read_local("books/test_dict.json")
        print("字典内容:", dict_content)
        print("类型:", type(dict_content))
    
    asyncio.run(test())
