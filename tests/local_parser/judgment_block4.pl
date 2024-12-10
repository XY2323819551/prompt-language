
IF $weather == "晴天":
   @send_email(
        "user@example.com",
        $health_advice
    ) -> email_result
elif $weather == "雪天":
    @send_email("user@example.com", $health_advice) -> email_result
END

