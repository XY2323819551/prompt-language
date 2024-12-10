import os
import asyncio
from prompt_language.parser.local_parser import JudgmentParser
from prompt_language.config import GlobalVariablePool


class MockVariablePool(GlobalVariablePool):
    """Mock的变量池，用于测试"""
    
    def __init__(self, test_case: str):
        super().__init__()
        if test_case == "case1_if":
            # 测试用例1 - IF分支
            self.variables = {
                "advice_type": "运动建议",
                "test_data": {
                    "cities": ["上海", "北京", "深圳"]
                },
                "city_weather": {
                    "status": "晴天"
                },
                "current_weather": {
                    "temperature": 25,
                    "humidity": 60
                }
            }
        elif test_case == "case1_elif":
            # 测试用例1 - ELIF分支
            self.variables = {
                "advice_type": "饮食建议",
                "current_weather": {
                    "temperature": 25,
                    "humidity": 60
                }
            }
        elif test_case == "case1_else":
            # 测试用例1 - ELSE分支
            self.variables = {
                "advice_type": "其他建议",
                "current_weather": {
                    "temperature": 25,
                    "humidity": 60
                }
            }
        elif test_case == "case2_if":
            # 测试用例2 - IF分支（高温高湿）
            self.variables = {
                "current_weather": {
                    "temperature": {
                        "current": 35
                    },
                    "humidity": 85,
                    "wind_speed": 3
                }
            }
        elif test_case == "case2_elif":
            # 测试用例2 - ELIF分支（低温大风）
            self.variables = {
                "current_weather": {
                    "temperature": {
                        "current": 5
                    },
                    "humidity": 50,
                    "wind_speed": 8
                }
            }
        elif test_case == "case2_else":
            # 测试用例2 - ELSE分支（普通天气）
            self.variables = {
                "current_weather": {
                    "temperature": {
                        "current": 25
                    },
                    "humidity": 60,
                    "wind_speed": 3
                }
            }
        elif test_case == "case3_if":
            # 测试用例3 - IF分支（晴天）
            self.variables = {
                "weather": "晴天",
                "health_advice": "今天是个好天气"
            }
        elif test_case == "case3_else":
            # 测试用例3 - 不命中条件
            self.variables = {
                "weather": "阴天",
                "health_advice": "今天是个好天气"
            }
        elif test_case == "case4_if":
            # 测试用例4 - IF分支（晴天）
            self.variables = {
                "weather": "晴天",
                "health_advice": "今天是个好天气"
            }
        elif test_case == "case4_elif":
            # 测试用例4 - ELIF分支（雪天）
            self.variables = {
                "weather": "雪天",
                "health_advice": "今天是个好天气"
            }
        elif test_case == "case4_else":
            # 测试用例4 - 不命中条件
            self.variables = {
                "weather": "阴天",
                "health_advice": "今天是个好天气"
            }


async def test_judgment_parser():
    """测试判断语句解析器"""
    parser = JudgmentParser()
    
    print("\n" + "="*80)
    print("测试用例1: 基本的if-elif-else结构")
    print("="*80)
    
    with open('tests/local_parser/judgment_block1.pl', 'r', encoding='utf-8') as f:
        content1 = f.read()
    
    # 测试IF分支 - "运动建议"
    print("\n" + "-"*40)
    print("测试1.1: IF分支 - 运动建议")
    print("-"*40)
    print("\n原始statement:")
    print(content1)
    mock_pool1_if = MockVariablePool("case1_if")
    result1_if = await parser.parse(content1, mock_pool1_if)
    print(f"\n条件值: \n{result1_if.condition_value}")
    print("\n语句块:\n")
    print(result1_if.statement)
    assert result1_if.condition_value == '$advice_type == "运动建议"'
    
    # 测试ELIF分支 - "饮食建议"
    print("\n" + "-"*40)
    print("测试1.2: ELIF分支 - 饮食建议")
    print("-"*40)
    print("\n原始statement:")
    print(content1)
    mock_pool1_elif = MockVariablePool("case1_elif")
    result1_elif = await parser.parse(content1, mock_pool1_elif)
    print(f"\n条件值: \n{result1_elif.condition_value}")
    print("\n语句块:\n")
    print(result1_elif.statement)
    assert result1_elif.condition_value == '$advice_type == "饮食建议"'
    
    # 测试ELSE分支 - "其他建议"
    print("\n" + "-"*40)
    print("测试1.3: ELSE分支 - 其他建议")
    print("-"*40)
    print("\n原始statement:")
    print(content1)
    mock_pool1_else = MockVariablePool("case1_else")
    result1_else = await parser.parse(content1, mock_pool1_else)
    print(f"\n条件值: \n{result1_else.condition_value}")
    print("\n语句块:\n")
    print(result1_else.statement)
    assert result1_else.condition_value == "other"
    
    print("\n" + "="*80)
    print("测试用例2: 多行条件表达式")
    print("="*80)
    
    with open('tests/local_parser/judgment_block2.pl', 'r', encoding='utf-8') as f:
        content2 = f.read()
    
    # 测试IF分支 - 高温高湿
    print("\n" + "-"*40)
    print("测试2.1: IF分支 - 高温高湿")
    print("-"*40)
    print("\n原始statement:")
    print(content2)
    mock_pool2_if = MockVariablePool("case2_if")
    result2_if = await parser.parse(content2, mock_pool2_if)
    print(f"\n条件值: \n{result2_if.condition_value}")
    print("\n语句块:\n")
    print(result2_if.statement)
    assert result2_if.condition_value == '${current_weather.temperature.current} > 30 and ${current_weather.humidity} > 80'
    
    # 测试ELIF分支 - 低温大风
    print("\n" + "-"*40)
    print("测试2.2: ELIF分支 - 低温大风")
    print("-"*40)
    print("\n原始statement:")
    print(content2)
    mock_pool2_elif = MockVariablePool("case2_elif")
    result2_elif = await parser.parse(content2, mock_pool2_elif)
    print(f"\n条件值: \n{result2_elif.condition_value}")
    print("\n语句块:\n")
    print(result2_elif.statement)
    assert result2_elif.condition_value == '${current_weather.temperature.current} < 10 and ${current_weather.wind_speed} > 5'
    
    # 测试ELSE分支 - 普通天气
    print("\n" + "-"*40)
    print("测试2.3: ELSE分支 - 普通天气")
    print("-"*40)
    print("\n原始statement:")
    print(content2)
    mock_pool2_else = MockVariablePool("case2_else")
    result2_else = await parser.parse(content2, mock_pool2_else)
    print(f"\n条件值: \n{result2_else.condition_value}")
    print("\n语句块:\n")
    print(result2_else.statement)
    assert result2_else.condition_value == "other"
    
    print("\n" + "="*80)
    print("测试用例3: 简单IF语句")
    print("="*80)
    
    with open('tests/local_parser/judgment_block3.pl', 'r', encoding='utf-8') as f:
        content3 = f.read()
    
    # 测试IF分支 - 晴天
    print("\n" + "-"*40)
    print("测试3.1: IF分支 - 晴天")
    print("-"*40)
    print("\n原始statement:")
    print(content3)
    mock_pool3_if = MockVariablePool("case3_if")
    result3_if = await parser.parse(content3, mock_pool3_if)
    print(f"\n条件值: \n{result3_if.condition_value}")
    print("\n语句块:\n")
    print(result3_if.statement)
    assert result3_if.condition_value == '$weather == "晴天"'
    
    # 测试不命中条件的情况
    print("\n" + "-"*40)
    print("测试3.2: 不命中任何条件")
    print("-"*40)
    print("\n原始statement:")
    print(content3)
    mock_pool3_else = MockVariablePool("case3_else")
    result3_else = await parser.parse(content3, mock_pool3_else)
    print(f"\n条件值: \n{result3_else.condition_value}")
    print("\n语句块:\n")
    print(result3_else.statement)
    assert result3_else.condition_value == "other"
    assert result3_else.statement == "none"
    
    print("\n" + "="*80)
    print("测试用例4: IF-ELIF语句")
    print("="*80)
    
    with open('tests/local_parser/judgment_block4.pl', 'r', encoding='utf-8') as f:
        content4 = f.read()
    
    # 测试IF分支 - 晴天
    print("\n" + "-"*40)
    print("测试4.1: IF分支 - 晴天")
    print("-"*40)
    print("\n原始statement:")
    print(content4)
    mock_pool4_if = MockVariablePool("case4_if")
    result4_if = await parser.parse(content4, mock_pool4_if)
    print(f"\n条件值: \n{result4_if.condition_value}")
    print("\n语句块:\n")
    print(result4_if.statement)
    assert result4_if.condition_value == '$weather == "晴天"'
    
    # 测试ELIF分支 - 雪天
    print("\n" + "-"*40)
    print("测试4.2: ELIF分支 - 雪天")
    print("-"*40)
    print("\n原始statement:")
    print(content4)
    mock_pool4_elif = MockVariablePool("case4_elif")
    result4_elif = await parser.parse(content4, mock_pool4_elif)
    print(f"\n条件值: \n{result4_elif.condition_value}")
    print("\n语句块:\n")
    print(result4_elif.statement)
    assert result4_elif.condition_value == '$weather == "雪天"'
    
    # 测试不命中条件的情况
    print("\n" + "-"*40)
    print("测试4.3: 不命中任何条件")
    print("-"*40)
    print("\n原始statement:")
    print(content4)
    mock_pool4_else = MockVariablePool("case4_else")
    result4_else = await parser.parse(content4, mock_pool4_else)
    print(f"\n条件值: \n{result4_else.condition_value}")
    print("\n语句块:\n")
    print(result4_else.statement)
    assert result4_else.condition_value == "other"
    assert result4_else.statement == "none"
    
    print("\n" + "="*80)
    print("所有测试用例执行完成")
    print("="*80)


if __name__ == "__main__":
    asyncio.run(test_judgment_parser())
