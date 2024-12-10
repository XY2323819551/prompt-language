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