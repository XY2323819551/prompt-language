import os
import aiofiles
import json
from typing import Union

async def save2local(content: Union[str, list, dict], filename: str) -> str:
    output_dir = "output"
    filepath = os.path.join(output_dir, filename)
    dirpath = os.path.dirname(filepath)
    
    if not os.path.exists(dirpath):
        os.makedirs(dirpath)
    
    # 将列表或字典转换为格式化的JSON字符串
    if isinstance(content, (list, dict)):
        content = json.dumps(content, ensure_ascii=False, indent=4)
    
    async with aiofiles.open(filepath, 'w', encoding='utf-8') as f:
        await f.write(content)
    
    return filepath

if __name__ == "__main__":
    import asyncio
    
    async def test():
        # 测试字符串
        text_content = "这是测试内容\n第二行内容"
        await save2local(text_content, "books/test_str.txt")
        
        # 测试列表
        list_content = ["item1", "item2", {"key": "value"}]
        await save2local(list_content, "books/test_list.json")
        
        # 测试字典
        dict_content = {
            "name": "test",
            "items": ["a", "b", "c"],
            "nested": {"x": 1, "y": 2}
        }
        await save2local(dict_content, "books/test_dict.json")
    
    asyncio.run(test())
