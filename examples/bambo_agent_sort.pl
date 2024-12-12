@agent(
    type="bambo", 
    task="请帮我生成一段选择排序的代码，调用代码执行器运行生成的代码，基于结果分析一下选择排序的特点", 
    roles = {
        "finance_expert": "金融专家",
        "law_expert": "法律专家",
        "medical_expert": "医疗专家",
        "computer_expert": "计算机专家",
    },
    tools=["code_execute", "get_weather"]
) -> sort_process

