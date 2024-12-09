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

FOR $city in ${test_data.cities}:
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

IF ${current_weather.temperature.current} > 30:
    生成一段关于防暑的建议 -> health_advice
    @send_email("user@example.com", $health_advice) -> email_result
elif ${current_weather.temperature.current} < 10:
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

@exit(msg="高级语句测试完成！")
