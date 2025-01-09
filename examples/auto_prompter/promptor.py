import asyncio
import os
import sys

# 将项目根目录添加到Python路径
root_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.append(root_dir)

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
        "benchmark": benchmark,
        "analyze_badcase": analyze_badcase,
        "prompt_optimizer": prompt_optimizer,
        "log2excelpic": log2excelpic,
        "meta_prompt": meta_prompt
    }
    
    # 初始化变量
    variables = {
        "task": "找出符合条件的人员，回答尽量精炼。问题：{{query}}\n参考信息：{{content}}\n",
        "model_name": "gemini",
        "dataset": "user_search_test",
        "acc_results": [],
        "suggestions": [],
        "prompts": []
    }
    
    await executor.init_execute(variables, tools)
    # 测试
    file_path = "/Users/zhangxiaoyu/Desktop/WorkSpace/prompt-language/examples/auto_prompter/promptor.pl"
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

