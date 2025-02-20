import asyncio
from typing import List, Optional
import os
from dotenv import load_dotenv
from .bing import bing_search
from .google import google_search
# from .duckduckgo_proxy import duckduckgo_search
from .wikipedia import wikipedia_search
from prompt_language.utils.model_factory.deepseek_r1 import get_model_response_v3


load_dotenv()

async def _collect_search_results(query: str) -> List[str]:
    tasks = [
        bing_search(query),
        google_search(query),
        # duckduckgo_search(query),
        wikipedia_search(query)
    ]
    
    results = []
    completed_tasks = await asyncio.gather(*tasks, return_exceptions=True)
    
    for task_result in completed_tasks:
        if isinstance(task_result, Exception):
            continue
        if isinstance(task_result, list):
            results.extend(task_result)
        elif isinstance(task_result, str) and task_result.strip():
            results.append(task_result)
    
    return results

async def _summarize_results(results: List[str], query: str) -> str:
    
    results="\n\n".join(results)
    results=results[:6000]
    if not results:
        return "未找到相关搜索结果"
    
    prompt = f"""任务说明：
你的任务是根据以下输入内容阅读并分析网页：当前搜索问题和已搜索的网页。你的目标是从已搜索的网页中提取与当前搜索问题相关且有用的信息，以继续对原始问题进行推理。

指导原则：
分析已搜索的网页：
仔细审查每个已搜索网页的内容。
找出与当前搜索问题相关且能够辅助推理原始问题的事实信息。

提取相关信息：
从已搜索的网页中选择能够直接推进之前的推理步骤的信息。
确保提取的信息准确且相关。

输出格式：
如果网页提供了对当前搜索问题有用的信息： 按照以下格式呈现信息。 
[有用的信息]
如果网页没有提供任何对当前搜索问题有用的信息： 输出以下文本。
未找到有用信息。

输入内容：
当前搜索问题：
{query}
已搜索的网页：
{results}
现在，你应该根据当前搜索问题"{query}"和之前的推理步骤，分析每个网页并找到有用的信息。"""
    

    messages = [{"role":"user", "content":prompt}]
    all_content = ""
    async for chunk in get_model_response_v3(messages=messages):
        content = chunk.choices[0].delta.content if chunk.choices[0].delta.content else ""
        print(content, end='', flush=True)
        all_content += content
    return all_content

async def searchall(query: str) -> str:
    """统一的网络搜索接口
    
    这是对外提供的主要接口，它会：
    1. 调用多个搜索引擎进行并行搜索
    2. 收集所有搜索结果
    3. 使用大模型对结果进行智能总结
    
    Args:
        query (str): 搜索查询字符串
    
    Returns:
        str: 搜索结果的智能总结
        
    Example:
        ```python
        result = await websearch("李鸿章的历史评价")
        print(result)
        ```
    """
    results = await _collect_search_results(query)
    summary = await _summarize_results(results, query)
    return summary

if __name__ == "__main__":
    async def test():
        result = await searchall("李鸿章的历史评价")
        print(result)
    
    asyncio.run(test())


