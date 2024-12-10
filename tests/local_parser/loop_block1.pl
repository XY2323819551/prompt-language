
FOR $city in ["shanghai","beijing","shenzhen","guangzhou","hangzhou"]:
    @get_weather($city) -> city_weather
    根据${city_weather.status}写一首诗 -> weather_poem
    $weather_poem >> poems_collection
END
