import os
import asyncio
from prompt_language.parser.local_parser import LoopParser
from prompt_language.config import GlobalVariablePool


class MockVariablePool(GlobalVariablePool):
    """Mock的变量池，用于测试"""
    
    def __init__(self):
        super().__init__()
        # 初始化一些测试数据
        self.variables = {
            "test_data": {
                "questions": ["问题1", "问题2", "问题3"]
            },
            "testdata2": [
                ["列表1项目1", "列表1项目2"],
                ["列表2项目1", "列表2项目2"]
            ],
            "simple_list": ["简单项目1", "简单项目2", "简单项目3"]
        }


async def test_loop_parser():
    """测试循环语句解析器"""
    parser = LoopParser()
    mock_pool = MockVariablePool()
    
    # 读取测试文件
    test_dir = os.path.dirname(os.path.abspath(__file__))
    test_files = [f'loop_block{i}.pl' for i in range(1, 6)]
    
    for test_file in test_files:
        file_path = os.path.join(test_dir, test_file)
        print(f"\n测试文件: {test_file}")
        print("="*50)
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read().strip()
            
            if not content:  # 跳过空文件
                continue
                
            # 解析循环块
            loop_block = await parser.parse(content)
            
            # 获取实际的迭代目标
            iteration_target = await parser.get_iteration_target(loop_block.target, mock_pool)
            print("\n原始内容:")
            print(content)
            print("\n解析结果:")
            print(f"循环变量: {loop_block.variable}")
            print(f"目标表达式: {loop_block.target}")
            print(f"实际迭代值: {iteration_target}")
            print("\n循环体语句:")
            print(loop_block.statement)
            
        except FileNotFoundError:
            print(f"\n✗ 文件不存在: {test_file}")
        except Exception as e:
            print(f"\n✗ 测试失败: {str(e)}")
        
        print("="*50)


if __name__ == "__main__":
    asyncio.run(test_loop_parser())