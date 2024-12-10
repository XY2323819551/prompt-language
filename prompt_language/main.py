import asyncio
import os
from prompt_language.executor import Executor
from prompt_language.utils.tool_factory import (
    search_arxiv,
    get_arxiv_pdf_content,
    serpapi_search,
    get_weather,
    wikipedia_search,
    eat_food,
    send_email
)


async def main():
    executor = Executor()
    variables = {
        "city": "Shanghai",
        "topic": "AI",
        "email": "user_a@example.com"
    }
    tools = {
        "search_arxiv": search_arxiv,
        "search_web": serpapi_search,
        "get_weather": get_weather,
        "send_email": send_email
    }
    await executor.init_execute(variables, tools)
    
    prompt = """
    # 获取天气信息
    @get_weather($city) -> weather
    
    # 搜索AI相关论文
    @search_arxiv($topic) -> papers
    
    # 发送邮件
    @send_email($email, $papers) -> result
    """
    await executor.execute(prompt)


async def test_main():
    executor = Executor()
    variables = {
        "city": "Shanghai",
        "topic": "AI",
        "email": "user_a@example.com"
    }
    tools = {
        "search_arxiv": search_arxiv,
        "serpapi_search": serpapi_search,
        "get_weather": get_weather,
        "send_email": send_email,
        "wikipedia_search": wikipedia_search,
    }
    await executor.init_execute(variables, tools)
    
    prompt = """
@code(```json
{
    "tasks": ["翻译", "总结", "分析"],
    "content": "这是一段需要处理的文本内容"
}
```) -> task_data

FOR $task in ${task_data.tasks}:
    IF $task == "翻译":
        将${task_data.content}翻译成英文 -> en_result
        $en_result >> results
    elif $task == "总结":
        总结${task_data.content}的要点 -> summary_result
        $summary_result >> results
    else:
        分析${task_data.content}的关键信息 -> analysis_result
        $analysis_result >> results
    END
END

@exit(msg="高级语句测试完成！")
    """
    await executor.execute(prompt)


async def test_from_file():
    # 初始化执行器
    executor = Executor()
    
    # 注册工具
    tools = {
        "search_arxiv": search_arxiv,
        "serpapi_search": serpapi_search,
        "get_weather": get_weather,
        "send_email": send_email,
        "wikipedia_search": wikipedia_search,
        "eat_food": eat_food,
    }
    
    # 初始化变量
    variables = {
        "city": "Shanghai",
        "topic": "AI",
        "email": "user_a@example.com"
    }
    
    await executor.init_execute(variables, tools)
    
    # 读取测试文件
    file_path = "/Users/zhangxiaoyu/Desktop/WorkSpace/prompt-language/examples/testcase.pl"
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            prompt = f.read()
        
        # 执行测试文件内容
        await executor.execute(prompt)
        
    except FileNotFoundError:
        print(f"错误: 找不到文件 {file_path}")
    except Exception as e:
        print(f"执行出错: {str(e)}")


if __name__ == "__main__":
    # asyncio.run(main())
    # asyncio.run(test_main())
    asyncio.run(test_from_file())

