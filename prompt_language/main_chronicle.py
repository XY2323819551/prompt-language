import asyncio
import os
from prompt_language.executor import Executor
from prompt_language.utils.tool_factory import *
from prompt_language.utils.prompt_logger import logger
import logging


async def test_from_file():
    # 设置日志级别
    logger.logger.setLevel(logging.INFO)
    
    # 初始化执行器
    executor = Executor()
    
    # 注册工具
    tools = {
        "send_email": send_email,
        "deduplicate": deduplicate,
        "save2local": save2local,
        "read_local": read_local,

        "wikipedia_search": wikipedia_search,
        "bing_search": bing_search,
        "google_search": google_search,
        "duckduckgo_search": duckduckgo_search
    }
    
    # 初始化变量
    variables = {
        "city": "Shanghai",
        "topic": "AI",
        "email": "user_a@example.com"
    }
    
    await executor.init_execute(variables, tools)
    # 测试
    root_path = "/Users/zhangxiaoyu/Desktop/WorkSpace/prompt-language/examples/real_cases/"
    file_path = root_path + "chronicle0.pl"
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            prompt = f.read()
        await executor.execute(prompt)
        
    except FileNotFoundError:
        print(f"错误: 找不到文件 {file_path}")
    except Exception as e:
        print(f"执行出错: {str(e)}")


if __name__ == "__main__":
    asyncio.run(test_from_file())

