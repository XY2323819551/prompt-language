
@agent(
    type="bambo", 
    task="我是高考生，现在想要选专业，但是不知道选什么专业。请你介绍一下金融、法律和计算机三个专业分别有什么优点和缺点。", 
    roles = {"finance_expert": "金融专家","law_expert": "法律专家","medical_expert": "医疗专家","computer_expert": "计算机专家",},
) -> suggestion
