# -*- coding: utf-8 -*-
import pandas as pd
import asyncio
qa_data = pd.read_excel('prompt_language/utils/tool_factory/kbqa/qq_v2.xlsx')
qa_dict = dict(zip(qa_data['input'], qa_data['predict_result']))

async def ngql(query):
    """使用ngql工具获取问题的参考资料。答案比较可靠，可以优先调用该工具获取问题的资料。但是该工具返回结果有限，当该工具没有返回结果时，应该调用其他工具获取资料。
    Args:
        query (str): 当前问题。
    """ 
    return qa_dict.get(query, "抱歉，我没有找到相关答案")


async def test():
    # 测试
    questions = ["agent应用开发组有哪些人", "郭健康是谁"]
    for q in questions:
        answer = await ngql(q)
        print(f"\n问题: {q}")
        print(f"答案: {answer}")

if __name__ == "__main__":
    asyncio.run(test())