import os
import asyncio
from prompt_language.parser.local_parser import StatementParser
from prompt_language.config import GlobalVariablePool


class MockVariablePool(GlobalVariablePool):
    """Mock的变量池，用于测试"""
    
    def __init__(self):
        super().__init__()
        self.variables = {
            "sh_weather": {
                "temperature": {
                    "current": 25
                }
            },
            "weather_info": {
                "status": "晴天",
                "temperature": 28
            },
            "poem": "春天来了",
            "search_result": "Python基础教程",
            "person_info": {
                "name": "张三",
                "age": 25,
                "hobbies": ["reading", "swimming"]
            },
            "health_advice": "今天天气不错，适合户外运动",
            "city_weather": {
                "status": "晴天",
                "temperature": 26
            }
        }


async def test_statement_parser():
    """测试语句解析器"""
    parser = StatementParser()
    mock_pool = MockVariablePool()
    
    # 读取测试文件
    test_dir = os.path.dirname(os.path.abspath(__file__))
    test_file = os.path.join(test_dir, 'statement_block.pl')
    
    with open(test_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 按空行分割测试用例
    test_cases = [case.strip() for case in content.split('\n\n') if case.strip()]
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n{'='*80}")
        print(f"测试用例 {i}")
        print('='*80)
        
        print("\n原始语句:")
        print(test_case)
        
        result = await parser.parse(test_case, mock_pool)
        
        print("\n解析结果:")
        print(f"赋值方法: {result.assign_method}")
        print(f"结果变量名: {result.res_name}")
        print(f"语句内容:\n{result.statement}")
        
        # 基本验证
        if '->' in test_case:
            assert result.assign_method == '->'
        elif '>>' in test_case:
            assert result.assign_method == '>>'
        
        if result.assign_method:
            assert result.res_name is not None
            assert result.statement is not None


if __name__ == "__main__":
    asyncio.run(test_statement_parser())
