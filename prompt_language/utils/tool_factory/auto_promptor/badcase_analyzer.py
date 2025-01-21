import pandas as pd
from openai import OpenAI

client = OpenAI(
    api_key="sk-9efddec830e34a1d915ebb4af09d26fb",
    base_url="https://api.deepseek.com"
)

async def conclusion_analysis(analysis_collections:list, prompt_template:str):
    """总结分析结果"""
    analysis_collection_texts = ""
    for idx, ans in enumerate(analysis_collections):
        analysis_collection_texts += f"\n第{idx}个badcase的分析结果是：{ans}\n"
    
    prompt = f"""你是一位资深的提示词工程专家。请对以下badcase分析结果进行系统性总结，并提出改进建议。

当前场景信息：
1. 使用的LLM指令：
{prompt_template}

2. Badcase分析结果汇总：
{analysis_collection_texts}

请从以下维度进行分析和总结：

1. 错误模式归类：
   - 找出所有badcase中的共性问题
   - 对错误类型进行分类统计
   - 识别最关键和最频繁的问题

2. 根因分析：
   - 提示词设计缺陷：当前提示词的主要问题
   - 任务理解偏差：模型对任务的理解是否存在系统性偏差
   - 约束条件不足：是否缺少必要的约束或指导

3. 改进建议：
   - 核心修改：必须进行的关键改进
   - 约束补充：需要添加的具体约束条件
   - 格式优化：输出格式的改进建议

请用中文输出分析结果，注重以下要求：
1. 建议必须具体且可直接执行
2. 对每个改进建议说明其解决的具体问题
3. 按照优先级排序，突出最重要的改进点

# 输出格式
分条罗列最终的改进建议。
"""

    try:
        from prompt_language.utils.model_factory.gemini_model import get_model_response_gemini
        response = await get_model_response_gemini(contents=prompt)
        analysis_conclusion = response
    except:
        response = client.chat.completions.create(
            model="deepseek-chat",
            messages=[{
                "role": "user", 
                "content": prompt
            }],
            temperature=0.0,
            max_tokens=2000
        )
        analysis_conclusion = response.choices[0].message.content

    return analysis_conclusion

def fluency_critic_analysis(response):
    client = OpenAI(
            api_key="sk-9efddec830e34a1d915ebb4af09d26fb",
            base_url="https://api.deepseek.com"
    )
    prompt_template = """
你是一位专业的语言评估专家。请仔细分析以下文本，找出不流畅的部分并提供改进建议。

评估维度：
1. 语句通顺度：句子是否读起来自然流畅
2. 用词准确性：词语使用是否恰当、精准
3. 语法规范性：语法结构是否正确
4. 语言连贯性：句子之间的过渡是否自然

参考文本：
{{model_response}}

请对整体表达的改进方向给出建议。
"""
    prompt = prompt_template.replace('{{model_response}}', response)
    response = client.chat.completions.create(
        model="deepseek-chat",
        messages=[{
            "role": "user", 
            "content": prompt
        }],
        temperature=0.0,
        max_tokens=1000
    )
    print("\n当前case的流畅度改进建议\n")
    print(response.choices[0].message.content)
    return response.choices[0].message.content

def consistency_critic_analysis(response):
    client = OpenAI(
        api_key="sk-9efddec830e34a1d915ebb4af09d26fb",
        base_url="https://api.deepseek.com"
    )

    prompt_template = """
你是一位专业的逻辑分析专家。请仔细分析以下文本，找出不一致、矛盾的部分并提供改进建议。
参考文本：
{{model_response}}

请对整体表达的改进方向给出建议。
"""
    prompt = prompt_template.replace('{{model_response}}', response)
    response = client.chat.completions.create(
        model="deepseek-chat",
        messages=[{
            "role": "user", 
            "content": prompt
        }],
        temperature=0.0,
        max_tokens=1000
    )
    print("\n当前case的一致性改进建议\n")
    print(response.choices[0].message.content)
    return response.choices[0].message.content


async def analyze_badcase(prompt_template:str="", log_file_path="output/benchmark_user_search_result.xlsx"):
    """分析badcase并给出改进建议"""
    # 读取日志文件
    df = pd.read_excel(log_file_path)
    
    # 提取需要的列
    questions = df["questions"].tolist()
    gold_answers = df["gold_answers"].tolist()
    llm_responses = df["llm_responses"].tolist()
    llm_scores = df["llm_scores"].tolist()
    fluency_scores = df["fluency_scores"].tolist()
    consistency_scores = df["consistency_scores"].tolist()
    evidences = df["evidences"].tolist()

    fluency_score_avg = round(sum(fluency_scores) / len(fluency_scores), 2)
    consistency_score_avg = round(sum(consistency_scores) / len(consistency_scores), 2)

    fluency_critic_flag, consistency_critic_flag = False, False
    if fluency_score_avg < 0.8:
        fluency_critic_flag = True
    if consistency_score_avg <0.8:
        consistency_critic_flag = True

    
    # 分析提示词模板
    analysis_prompt_template = """你是一位专业的提示词分析专家。请分析以下问答对中存在的问题，并给出改进建议。

输入信息：
1. 原始问题：{{question}}
2. 参考资料：{{evidence}}
3. 期望答案/关键词：{{gold_answer}}
4. 模型回答：{{llm_response}}
5. 当前提示词：{prompt_template}

请按以下格式输出分析结果：

## 问题分析
1. 答案质量问题：
   - [分析模型答案与期望答案的差异]
   - [分析模型是否正确使用了参考资料]
   - [指出答案中的错误或遗漏]

2. 原因分析：
   - [指出导致问题的核心原因]
   - [分析当前提示词的不足之处]

## 改进建议
- [给出3-5条具体的改进建议]
- [说明每条建议预期解决的问题]

评估标准：
1. 建议必须具体且可执行
2. 建议应针对性解决已发现的问题
3. 避免泛泛而谈，需要有明确的改进方向"""
    
    analysis_collections = []
    # 遍历所有case进行分析
    for idx, score in enumerate(llm_scores):
        if score != 1:  # 只分析错误的case
            print(f"\n{'='*50} Badcase {idx+1} {'='*50}")
            
            # 构造分析提示词
            prompt = analysis_prompt_template.replace("{{question}}", str(questions[idx])) \
                                          .replace("{{gold_answer}}", str(gold_answers[idx])) \
                                          .replace("{{llm_response}}", str(llm_responses[idx])) \
                                          .replace("{{evidence}}", str(evidences[idx]))
            
            # 调用大模型分析
            try:
                response = client.chat.completions.create(
                    model="deepseek-chat",
                    messages=[{
                        "role": "user", 
                        "content": prompt
                    }],
                    temperature=0.0,
                    max_tokens=2000
                )
                
                analysis = response.choices[0].message.content
                if fluency_critic_flag and fluency_scores[idx] < 0.8:
                    fluency_critic_analysis = fluency_critic_analysis(llm_responses[idx])
                    analysis = analysis + "\n流畅度改进建议：" + fluency_critic_analysis
                if consistency_critic_flag and consistency_scores[idx] < 0.8:
                    consistency_critic_analysis = consistency_critic_analysis(llm_responses[idx])
                    analysis = analysis + "\n一致性改进建议：" + consistency_critic_analysis
                
                
                analysis_collections.append(analysis)
                
                print(f"原始问题：{questions[idx]}\n")
                print(f"答案需要包含的关键词：{gold_answers[idx]}\n")
                print(f"模型回答：{llm_responses[idx]}\n")
                print(f"参考资料：{evidences[idx]}\n")
                print(f"\n分析结果：\n{analysis}\n")
                
            except Exception as e:
                print(f"分析过程中出错: {str(e)}")
                continue

    conclusion = await conclusion_analysis(analysis_collections, prompt_template)
    print(f"=========================最终的修改建议如下 =================================\n")
    print(conclusion)
    print(f"=========================最终的修改建议 =================================\n")
    return conclusion


async def main():
    # 基本功能测试
    prompt_template = "找出符合条件的人员，回答尽量精炼。问题：{{query}}\n参考信息：{{content}}\n"
    conclusion_analysis = await analyze_badcase(prompt_template=prompt_template, log_file_path="output/benchmark_user_search_result.xlsx")
    print(conclusion_analysis)


if __name__ == '__main__':
    import asyncio
    asyncio.run(main())

