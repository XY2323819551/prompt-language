import os
import pytest
import asyncio
from prompt_language.parser.global_parser import GlobalParser

async def test_parser():
    """测试解析器"""
    # 测试用例目录
    test_dir = os.path.dirname(os.path.abspath(__file__))
    
    # 遍历目录下的所有.pl文件
    for filename in os.listdir(test_dir):
        if filename.endswith('.pl'):
            file_path = os.path.join(test_dir, filename)
            print(f"\n测试文件: {filename}")
            
            # 读取文件内容
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # 异步解析内容
            parser = GlobalParser()
            block_queue = await parser.parse(content)
            
            # 打印解析结果
            print("\n解析结果:")
            block_number = 1
            
            # 从队列中获取并打印所有代码块
            while not block_queue.empty():
                block = await block_queue.get()
                print(f"\n---------Block {block_number}:----------")
                print(f"Type: {block.block_type}")
                print(f"Statement:\n{block.statement}")
                block_queue.task_done()
                block_number += 1
            
            print("\n" + "="*50)

@pytest.mark.asyncio
async def test_parser_async():
    """异步测试入口"""
    await test_parser()

if __name__ == '__main__':
    asyncio.run(test_parser())
