import pandas as pd
from openai import OpenAI

client = OpenAI(
    api_key="sk-9efddec830e34a1d915ebb4af09d26fb",
    base_url="https://api.deepseek.com"
)

def conclusion_analysis(analysis_collections:list, prompt_template:str):
    """总结分析结果"""
    analysis_collections = "\n".join(analysis_collections)
    prompt = f"""请总结以下分析结果，简要的总结出可以scale的建议，并给出改进原始prompt的建议和给出该建议的原因：

分析结果：
{analysis_collections}

原始的prompt是：
{prompt_template}

请用中文回答。"""
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
    
async def analyze_badcase(prompt_template:str="", log_file_path="output/benchmark_user_search_result.xlsx"):
    """分析badcase并给出改进建议"""
    # 读取日志文件
    df = pd.read_excel(log_file_path)
    
    # 提取需要的列
    questions = df["questions"].tolist()
    gold_answers = df["gold_answers"].tolist()
    llm_responses = df["llm_responses"].tolist()
    llm_scores = df["llm_scores"].tolist()
    evidences = df["evidences"].tolist()
    
    # 分析提示词模板
    analysis_prompt_template = f"""请分析以下问答对的错误原因并给出改进建议：

原始问题：{{question}}

标准答案：{{gold_answer}}

模型回答：{{llm_response}}
·
参考资料：{{evidence}}

请从以下几个方面进行分析：
1. 对比标准答案和模型回答的差异
2. 根据参考资料分析错误原因
3. 总结模型产生错误的根本原因
4. 给出改进后的提示词建议，让模型能够输出正确答案
原始的提示词是：
{prompt_template}

请用中文回答。"""
    
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
                analysis_collections.append(analysis)
                

                print(f"原始问题：{questions[idx]}\n")
                print(f"标准答案：{gold_answers[idx]}\n")
                print(f"模型回答：{llm_responses[idx]}\n")
                print(f"参考资料：{evidences[idx]}\n")
                print(f"\n分析结果：\n{analysis}\n")
                
            except Exception as e:
                print(f"分析过程中出错: {str(e)}")
                continue

    conclusion = conclusion_analysis(analysis_collections, prompt_template)
    print(f"=========================最终的修改建议是: =================================\n")
    print(conclusion)
    print(f"=========================最终的修改建议是: =================================\n")
    return conclusion


async def main():
    # 基本功能测试
    prompt_template = "找出符合条件的人员，回答尽量精炼。问题：{{query}}\n参考信息：{{content}}\n"
    conclusion_analysis = await analyze_badcase(prompt_template=prompt_template, log_file_path="output/benchmark_user_search_result.xlsx")
    print(conclusion_analysis)


if __name__ == '__main__':
    import asyncio
    asyncio.run(main())

