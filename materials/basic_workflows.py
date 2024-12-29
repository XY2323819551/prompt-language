import re
import asyncio
from concurrent.futures import ThreadPoolExecutor
from typing import List, Dict, Callable
from prompt_language.utils.model_factory.model_factory import get_model_response
from prompt_language.utils.model_factory.gemini_model import get_model_response_gemini

"""
## Basic Multi-LLM Workflows

This notebook demonstrates three simple multi-LLM workflows. They trade off cost or latency for potentially improved task performances:

1. **Prompt-Chaining**: Decomposes a task into sequential subtasks, where each step builds on previous results
2. **Parallelization**: Distributes independent subtasks across multiple LLMs for concurrent processing
3. **Routing**: Dynamically selects specialized LLM paths based on input characteristics

Note: These are sample implementations meant to demonstrate core concepts - not production code.
"""


def extract_xml(text: str, tag: str) -> str:
    """
    Extracts the content of the specified XML tag from the given text. Used for parsing structured responses 

    Args:
        text (str): The text containing the XML.
        tag (str): The XML tag to extract content from.

    Returns:
        str: The content of the specified XML tag, or an empty string if the tag is not found.
    """
    match = re.search(f'<{tag}>(.*?)</{tag}>', text, re.DOTALL)
    return match.group(1) if match else ""

async def chain(input: str, prompts: List[str]) -> str:
    """按顺序链接多个LLM调用,在步骤之间传递结果"""
    result = input
    for i, prompt in enumerate(prompts, 1):
        print(f"\n步骤 {i}:")
        result = await get_model_response_gemini(contents=f"{prompt}\n输入: {result}")
        print(result)
    return result

async def parallel(prompt: str, inputs: List[str]) -> List[str]:
    """使用相同的提示并发处理多个输入"""
    tasks = [get_model_response_gemini(contents=f"{prompt}\n输入: {x}") for x in inputs]
    return await asyncio.gather(*tasks)

async def route(input: str, routes: Dict[str, str]) -> str:
    """使用内容分类将输入路由到专门的提示"""
    print(f"\n可用路由: {list(routes.keys())}")
    selector_prompt = f"""
    分析输入并从以下选项中选择最合适的支持团队: {list(routes.keys())}
    首先解释你的推理,然后用这种XML格式提供你的选择:

    <reasoning>
    简要解释为什么这个工单应该路由到特定团队。
    考虑关键术语、用户意图和紧急程度。
    </reasoning>

    <selection>
    所选团队名称
    </selection>

    输入: {input}""".strip()
    
    route_response = await get_model_response_gemini(contents=selector_prompt)
    reasoning = extract_xml(route_response, 'reasoning')
    route_key = extract_xml(route_response, 'selection').strip().lower()
    
    print("路由分析:")
    print(reasoning)
    print(f"\n选定路由: {route_key}")
    
    selected_prompt = routes[route_key]
    return await get_model_response_gemini(contents=f"{selected_prompt}\n输入: {input}")




async def main():
    # # 示例1: 用于结构化数据提取和格式化的链式工作流
    # data_processing_steps = [
    #     """从文本中仅提取数值及其相关指标。
    #     每行格式为'值: 指标'。
    #     示例格式:
    #     92: 客户满意度
    #     45%: 收入增长""",
        
    #     """尽可能将所有数值转换为百分比。
    #     如果不是百分比或点数,则转换为小数(例如,92点 -> 92%)。
    #     每行保持一个数字。
    #     示例格式:
    #     92%: 客户满意度
    #     45%: 收入增长""",
        
    #     """按数值降序排列所有行。
    #     保持每行'值: 指标'的格式。
    #     示例:
    #     92%: 客户满意度
    #     87%: 员工满意度""",
        
    #     """将排序后的数据格式化为markdown表格,列为:
    #     | 指标 | 值 |
    #     |:--|--:|
    #     | 客户满意度 | 92% |"""
    # ]

    # report = """
    # 第三季度业绩总结:
    # 我们的客户满意度得分本季度上升至92分。
    # 收入同比增长45%。
    # 在主要市场的市场份额现在为23%。
    # 客户流失率从8%降至5%。
    # 新用户获取成本为每用户43美元。
    # 产品采用率提高到78%。
    # 员工满意度为87分。
    # 运营利润率提高到34%。
    # """

    # print("\n输入文本:")
    # print(report)
    # formatted_result = await chain(report, data_processing_steps)
    # print(formatted_result)





    # 示例2: 用于利益相关者影响分析的并行工作流
    # stakeholders = [
    #     """客户:
    #     - 价格敏感
    #     - 想要更好的技术
    #     - 环保意识""",
        
    #     """员工:
    #     - 工作安全担忧
    #     - 需要新技能
    #     - 想要明确方向""",
        
    #     """投资者:
    #     - 期望增长
    #     - 要求成本控制
    #     - 风险关注""",
        
    #     """供应商:
    #     - 产能限制
    #     - 价格压力
    #     - 技术转型"""
    # ]

    # impact_results = await parallel(
    #     """分析市场变化将如何影响这个利益相关者群体。
    #     提供具体影响和建议行动。
    #     使用清晰的章节和优先级格式化。""",
    #     stakeholders
    # )

    # for result in impact_results:
    #     print(result)







    # # 示例3: 用于客户支持工单处理的路由工作流
    support_routes = {
        "billing": """你是一位计费支持专家。遵循以下指导:
        1. 始终以"计费支持回复:"开头
        2. 首先确认具体的计费问题
        3. 清楚解释任何费用或差异
        4. 列出具体后续步骤和时间表
        5. 如果相关,以付款选项结束
        
        保持专业但友好的回复。
        
        输入: """,
        
        "technical": """你是一位技术支持工程师。遵循以下指导:
        1. 始终以"技术支持回复:"开头
        2. 列出解决问题的确切步骤
        3. 如果相关,包括系统要求
        4. 提供常见问题的解决方法
        5. 以升级路径结束(如果需要)
        
        使用清晰的编号步骤和技术细节。
        
        输入: """,
        
        "account": """你是一位账户安全专家。遵循以下指导:
        1. 始终以"账户支持回复:"开头
        2. 优先考虑账户安全和验证
        3. 提供清晰的账户恢复/更改步骤
        4. 包括安全提示和警告
        5. 设定明确的解决时间预期
        
        保持严肃的安全导向语气。
        
        输入: """,
        
        "product": """你是一位产品专家。遵循以下指导:
        1. 始终以"产品支持回复:"开头
        2. 专注于功能教育和最佳实践
        3. 包括具体使用示例
        4. 链接到相关文档部分
        5. 建议可能有帮助的相关功能
        
        使用教育性和鼓励性的语气。
        
        输入: """
    }

    tickets = [
        """主题: 无法访问我的账户
        消息: 你好,我已经尝试登录一个小时了,但一直收到"密码无效"错误。
        我确信我使用的密码是正确的。你能帮我重新获得访问权限吗？这很紧急,因为我需要在今天结束前提交一份报告。
        - 约翰""",
        
        """主题: 信用卡上的意外收费
        消息: 你好,我刚刚注意到你们公司在我的信用卡上收取了49.99美元,但我认为
        我使用的是29.99美元的套餐。你能解释这笔费用并在有错误的情况下调整吗？
        谢谢,
        莎拉""",
        
        """主题: 如何导出数据？
        消息: 我需要将所有项目数据导出到Excel。我已经查看了文档但无法
        弄清楚如何进行批量导出。这可能吗？如果可以,你能指导我完成这些步骤吗？
        此致,
        迈克"""
    ]

    print("正在处理支持工单...\n")
    for i, ticket in enumerate(tickets, 1):
        print(f"\n工单 {i}:")
        print("-" * 40)
        print(ticket)
        print("\n回复:")
        print("-" * 40)
        response = await route(ticket, support_routes)
        print(response)

if __name__ == "__main__":
    asyncio.run(main()) 


