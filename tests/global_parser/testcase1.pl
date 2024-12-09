
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
@agent(type="chatgpt", task="根据${weather_info}生成一个笑话", tools={}) -> joke
@exit(msg="测试完成，正常退出！")

