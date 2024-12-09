请从以下人员信息中回答问题，选择符合条件的人员：

问题：{{query}}
人员信息：{{content}}
问题：{{query}}

# workflows
1. 识别用户问题中的筛选条件
2. 根据筛选条件逐个筛选人员信息
3. 人员信息中没有提到的条件，视为不满足。
4. 严格筛选符合全部条件的人员，并简要解释选择原因。如果筛选原因都一致，则合并筛选原因。

# Limitations
1. 若没有性别信息，则一律使用”他“
2. 没有出现的信息，例如部门、工作地点 -> test_prompt


@code(```json
{
    "cities": ["shanghai", "beijing", "shenzhen", "guangzhou"],
    "questions": [
        "Python是什么？",
        "机器学习入门",
        "深度学习基础"
    ]
}
```) -> test_data

FOR $city in [
    "shanghai",
    "beijing",
    "shenzhen",
    "guangzhou",
    "hangzhou"
]:
    @get_weather($city) -> city_weather
    根据${city_weather.status}写一首诗 -> weather_poem
    $weather_poem >> poems_collection
END

FOR $question in ${test_data.questions}:
    @serpapi_search($question) -> search_result
    总结一下$search_result -> summary
    $summary >> qa_collection
END

@get_weather("Shanghai") -> current_weather

IF ${current_weather.temperature.current} > 30 
   and ${current_weather.humidity} > 80:
    生成一段关于防暑的建议 -> health_advice
    @send_email(
        "user@example.com",
        $health_advice
    ) -> email_result
elif ${current_weather.temperature.current} < 10 
     and ${current_weather.wind_speed} > 5:
    生成一段关于防寒的建议 -> health_advice
    @send_email("user@example.com", $health_advice) -> email_result
else:
    生成一段关于适合外出活动的建议 -> health_advice
    @send_email("user@example.com", $health_advice) -> email_result
END

# 3.2 复杂条件判断
@condition_judge($health_advice, ["运动建议", "饮食建议", "着装建议"]) -> advice_type

IF $advice_type == "运动建议":
    FOR $city in ${test_data.cities}:
        @get_weather($city) -> city_weather
        IF ${city_weather.status} == "晴天":
            $city >> suitable_cities
        END
    END
    根据$suitable_cities生成运动场所推荐 -> sport_recommendation
elif $advice_type == "饮食建议":
    分析当前天气生成饮食建议 -> food_recommendation
else:
    根据$current_weather生成着装建议 -> clothing_recommendation
END

# 4. 混合使用示例
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


根据以下几个城市的天气情况：
北京：晴天，25度
上海：多云，23度
广州：小雨，28度
生成一篇天气分析报告，
包含温度对比和天气趋势 -> weather_analysis

# 6. code block - 多行测试
@code(```python
def process_weather_data(cities_data):
    result = {}
    for city, data in cities_data.items():
        temp = data.get('temperature', 0)
        humidity = data.get('humidity', 0)
        result[city] = {
            'comfort_index': temp * 0.8 + humidity * 0.2,
            'suitable_for_outdoor': temp > 15 and temp < 30
        }
    return result

weather_result = process_weather_data({
    'beijing': {'temperature': 25, 'humidity': 60},
    'shanghai': {'temperature': 23, 'humidity': 70},
    'guangzhou': {'temperature': 28, 'humidity': 85}
})
```) -> weather_processing_result

# 7. condition_judge block - 多行测试
@condition_judge(
    $weather_analysis,
    [
        "温度分析",
        "湿度分析",
        "空气质量分析",
        "天气趋势分析"
    ]
) -> analysis_type

# 8. exit block - 多行测试
@exit(
    msg="测试完成！\n"
    "所有语句类型都已验证\n"
    "包括多行情况"
)

# 9. function block - 多行测试
@serpapi_search(
    query="天气预报API",
    num_results=5,
    search_type="web"
) -> search_results

# 10. agent block - 多行测试
@agent(
    type="auto-decision",
    task="分析所有城市的天气数据，生成一份详细的天气报告，并通过邮件发送",
    tools={
        "weather": "@get_weather",
        "email": "@send_email",
        "analysis": "data_analysis"
    }
) -> weather_report_agent

# 11. 混合多行测试
@code(```json
{
    "cities": [
        "shanghai",
        "beijing",
        "shenzhen",
        "guangzhou"
    ],
    "analysis_types": [
        "temperature",
        "humidity",
        "wind",
        "aqi"
    ]
}
```) -> analysis_config

FOR $city in ${analysis_config.cities}:
    FOR $type in ${analysis_config.analysis_types}:
        IF $type == "temperature":
            分析${city}的温度变化趋势，
            包括日间和夜间温差，
            以及未来三天的温度走势 -> temp_analysis
            $temp_analysis >> city_analysis
        elif $type == "humidity":
            分析${city}的湿度情况，
            结合温度给出舒适度评估 -> humidity_analysis
            $humidity_analysis >> city_analysis
        else:
            综合分析${city}的${type}指标，
            给出相应的建议 -> other_analysis
            $other_analysis >> city_analysis
        END
    END
END

@exit(msg="多行测试用例全部完成！")
