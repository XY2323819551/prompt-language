import asyncio
from prompt_language.utils.model_factory.deepseek_r1 import get_model_response_v3_static, get_model_response_r1_static


prompt = """
当前问题为：
{{query}}
 
 
历史对话信息为：
{{history_message}}
 
# 步骤
步骤1. 如果历史对话信息和当前问题无关，或无法改写，请忽略后续步骤，直接返回：【重写后的问题】{{query}}。
步骤2. 如果可以改写，则先识别当前问题中的主语和所有的指代，输出你的答案。
步骤3. 从历史对话信息中找出步骤2中涉及的主语或指代的具体内容，要忠于原文，不要少任何一个字。输出你的答案
步骤4. 结合步骤2和步骤3的结果，将你找到的具体的主语或指代替换到当前问题中（当前问题是【{{query}}。重写后的问题尽量简短。输出重写后的问题，输出格式为：【重写后的问题】xxx
 
# 注意事项
1. 你只需要补充当前问题的主语和指代信息即可。
2. 你有足够的时间，请认真思考后回答。
"""


async def query_rewrite(query, history_messages=[]):
    """根据历史对话信息重写当前子问题，补充主语和指代信息。如果当前需要回答的子问题不是第一个子问题，就需要在调用该工具对子问题进行补充。
    Args:
        query (str): 需要重写的原始问题。
    """
    # 将历史消息列表转换为字符串
    # history_str = "\n".join(history_messages) if history_messages else "无历史对话信息"
    history_str = str(history_messages)

    
    # 替换prompt中的占位符
    current_prompt = prompt.replace("{{query}}", query).replace("{{history_message}}", history_str)
    
    # 调用模型获取回答
    messages = [
        {"role":"system", "content":"你是一个问题重写专家，可以根据历史对话信息，对当前问题的主语和指代进行补充完善，生成一个语义明确、没有指代的问题。"},
        {"role":"user", "content":current_prompt}
    ]
    response = await get_model_response_v3_static(messages=messages)
    # 提取重写后的问题
    if "【重写后的问题】" in response:
        rewritten_query = response.split("【重写后的问题】")[-1].strip()
        return rewritten_query
    return query

async def test():
    # 测试用例1：无历史信息的情况
    # query1 = "他是谁？"
    # print("\n测试1 - 无历史信息:")
    # print("原始问题:", query1)
    # rewritten_query = await query_rewrite(query1)
    # print("重写结果:", rewritten_query)
    
    # 测试用例2：有历史信息的情况
    query2 = "职位呢？"
    history = [
        {"role":"user", "content":"张小宇在哪里工作？"},
        {"role":"assistant", "content":"他在Agent应用开发组工作"}
    ]
    print("\n测试2 - 有历史信息:")
    print("原始问题:", query2)
    print("历史信息:", history)
    rewritten_query = await query_rewrite(query2, history)
    print("重写结果:", rewritten_query)

if __name__ == "__main__":
    asyncio.run(test())
