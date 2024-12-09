import asyncio
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
        "search_web": serpapi_search,
        "get_weather": get_weather,
        "send_email": send_email
    }
    await executor.init_execute(variables, tools)
    
    prompt = """
    查询一下上海今天的天气 -> weather_info
根据${weather_info.temperature}写一首诗 -> poem
把$poem翻译成英文 -> en_poem
@serpapi_search("Python教程") -> search_result
@get_weather("Shanghai") -> sh_weather
@wikipedia_search($search_result) -> wiki_content
@code(```python
def process_temperature(temp):
    return f"当前温度是{temp}度"
result = process_temperature(${sh_weather.temperature.current})
```) -> temp_result
@code(```json
{
    "name": "张三",
    "age": 25,
    "hobbies": ["reading", "swimming"]
}
```) -> person_info
@code(计算${person_info.age}加上10是多少) -> age_after_10
@condition_judge($weather_info, ["晴天", "雨天", "阴天"]) -> weather_condition
    """
    await executor.execute(prompt)



if __name__ == "__main__":
    # asyncio.run(main())
    asyncio.run(test_main())

