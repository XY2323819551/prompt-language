import asyncio
from prompt_language.blocks.agent_block import AgentBlock


async def test_parse_agent_params():
    """测试agent参数解析"""
    print("\n开始测试 agent 参数解析...")
    agent_block = AgentBlock()
    
    # 测试用例1: 完整参数
    print("\n测试用例1: 完整参数")
    print("-" * 50)
    statement1 = """@agent(
    type="bambo", 
    task="请帮我生成一段选择排序的代码，调用代码执行器运行生成的代码，基于结果分析一下选择排序的特点", 
    roles = {
        "finance_expert": "金融专家",
        "law_expert": "法律专家",
        "medical_expert": "医疗专家",
        "computer_expert": "计算机专家",
    },
    tools=["code_execute"]
)"""
    print("输入语句:")
    print(statement1)
    
    result1 = agent_block._parse_agent_params(statement1)
    print("\n解析结果:")
    print(f"type: {result1['type']}")
    print(f"task: {result1['task']}")
    print(f"roles: {result1['roles']}")
    print(f"tools: {result1['tools']}")
    
    # 测试用例2: 只有必要参数
    print("\n测试用例2: 只有必要参数")
    print("-" * 50)
    statement2 = """@agent(
    type="bambo", 
    task="请帮我生成一段选择排序的代码，调用代码执行器运行生成的代码，基于结果分析一下选择排序的特点"
)"""
    print("输入语句:")
    print(statement2)
    
    result2 = agent_block._parse_agent_params(statement2)
    print("\n解析结果:")
    print(f"type: {result2['type']}")
    print(f"task: {result2['task']}")
    print(f"roles: {result2['roles']}")
    print(f"tools: {result2['tools']}")
    
    # 测试用例3: 部分参数
    print("\n测试用例3: 部分参数")
    print("-" * 50)
    statement3 = """@agent(
    task="请帮我生成一段选择排序的代码，调用代码执行器运行生成的代码，基于结果分析一下选择排序的特点", 
    tools=["code_execute"]
)"""
    print("输入语句:")
    print(statement3)
    
    result3 = agent_block._parse_agent_params(statement3)
    print("\n解析结果:")
    print(f"type: {result3['type']}")
    print(f"task: {result3['task']}")
    print(f"roles: {result3['roles']}")
    print(f"tools: {result3['tools']}")
    
    print("\n所有测试完成!")


if __name__ == "__main__":
    asyncio.run(test_parse_agent_params()) 