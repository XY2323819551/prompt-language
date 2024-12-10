
@get_weather("Shanghai") -> current_weather

IF ${current_weather.temperature.current} > 30 
   and ${current_weather.humidity} > 80:
    生成一段关于防暑的建议 -> health_advice
    @send_email(
        "user@example.com",
        $health_advice
    ) -> email_result
elif ${current_weather.temperature.current} < 10 
     and ${current_weather.wind.speed} > 5:
    生成一段关于防寒的建议 -> health_advice
    @send_email("user@example.com", $health_advice) -> email_result
else:
    生成一段关于适合外出活动的建议 -> health_advice
    @send_email("user@example.com", $health_advice) -> email_result
END
