import os
import random
import pandas as pd
from typing import List
from openai import OpenAI


"""
1、根据acc中最大的值的索引index值，去找到log_file_path文件夹下对应的excel文件，文件的名称为$item-iteration.xlsx，其中$item需要替换为具体的index值
2、读取excel文件中的questions, llm_responses, llm_contents，llm_scores，这4个列的内容
3、从llm_scores为1的case中，随机抽取3个case，存起来，作为正例的数据源
4、构造prompt，请求大模型，要求大模型根据question，和llm_response，以及指令prompt_template，生成解决问题的思考过程
"""

async def add_few_shot(prompts: List[str], acc: List[float], log_file_path: str) -> str:
    
    client = OpenAI(
        api_key="sk-9efddec830e34a1d915ebb4af09d26fb",
        base_url="https://api.deepseek.com"
    )
    # 步骤1: 找到最佳acc对应的excel文件
    best_acc_index = acc.index(max(acc))
    if isinstance(prompts, str):
        prompt_template = prompts
    else:
        prompt_template = prompts[best_acc_index]

    target_file = f"{best_acc_index+1}iteration.xlsx"
    file_path = os.path.join(log_file_path, target_file)
    
    # 步骤2: 读取指定列的内容
    df = pd.read_excel(file_path)
    data = {
        'questions': df['questions'].tolist(),
        'llm_responses': df['llm_responses'].tolist(),
        'llm_contents': df['llm_contents'].tolist(), 
        'llm_scores': df['llm_scores'].tolist()
    }
    
    # 步骤3: 从llm_scores为1的case中随机抽取10个正例
    positive_indices = [i for i, score in enumerate(data['llm_scores']) if score == 1]
    selected_indices = random.sample(positive_indices, min(10, len(positive_indices)))
    
    examples = []
    for idx in selected_indices:
        question = data['questions'][idx]
        llm_response = data['llm_responses'][idx]
        examples.append(f"======示例{idx+1}: \n问题: {question}\n回答: {llm_response}\n======")
    
    
    changed_prompt_template = (
        "你是一位 [提示词]优化专家，主要按照要求完成以下任务。\n"
        f"[提示词]: {prompt_template}\n"
        "如果上述提示词中包含了few-shot，请将few-shot的示例集去除（因为后续我会添加质量更高的few-shot示例集）然后返回去除了示例集之后的提示词，\n"
        "如果上述提示词中没有包含few-shot，请直接返回当前的提示词即可，不要作任何改动\n"
        "注意，仅仅返回提示词，不要返回任何其他内容\n"
    )
    from prompt_language.utils.model_factory.gemini_model import get_model_response_gemini
    response = await get_model_response_gemini(contents=changed_prompt_template)
    prompt_template = response
    

    critique_prompt = (
        "你是一位专家示例选择者，可以帮助选择合适的上下文示例来帮助最合适且最有能力的执行者解决问题。\n"
        "你还将获得用于解决此任务的提示词指令\n"
        f"[提示词]: {prompt_template}\n"
        "我正在尝试编写一个包含 3 个上下文示例的少样本提示词，以有效解决上述任务的任何问题。\n"
        f"我当前的 10 个上下文示例集是：{examples}\n\n"
        "请从示例类型的多样性、示例性质/特征的复杂性以及与整个示例集的相关性/兼容性等标准来分析、理解和创建任务示例。\n"
        "请输出所有可以用来改进整个示例选择集中每个单独示例的建议/改进意见。"
    )

    response = await get_model_response_gemini(contents=critique_prompt)
    critique_response = response

    # response = client.chat.completions.create(
    #     model="deepseek-chat",
    #     messages=[{
    #         "role": "user", 
    #         "content": critique_prompt
    #     }],
    #     temperature=0.0,
    #     max_tokens=2000
    # )
    # critique_response = response.choices[0].message.content


    print("\n============critique_response:============\n")
    print(critique_response)
    refinement_prompt = (
        "你是一位专家示例选择者，可以帮助选择合适的上下文示例来帮助执行者解决问题。\n"
        "你还将获得用于解决此任务的提示词指令\n"
        f"[提示词]: {prompt_template}\n\n"
        "我正在尝试编写一个包含 3 个上下文示例的少样本提示词，以有效解决上述任务的任何问题。\n"
        f"我当前的 10 个上下文示例集是：{examples}\n"
        "你还获得了一组可以用来改进整个示例选择集中每个单独示例的建议/改进意见：\n"
        f"[建议/改进]: {critique_response}\n"
        "基于以上信息，请巧妙地运用这些建议和改进意见，仔细创建新的 3 个示例集。\n"
        "请确保用 <START> 和 <END> 标签包裹每个示例。\n\n"
        "新示例必须严格遵循以下格式：\n\n"
        "[问题] 后跟示例的问题部分\n"
        "[答案] 后跟与答案相关的所有逻辑推理陈述。最终答案用\"<ANS_START>[答案]<ANS_END>\"表示\n\n"
        "[新示例]："
    )


    response = await get_model_response_gemini(contents=refinement_prompt)
    refinement_response = response
    
    # response = client.chat.completions.create(
    #     model="deepseek-chat",
    #     messages=[{
    #         "role": "user", 
    #         "content": refinement_prompt
    #     }],
    #     temperature=0.0,
    #     max_tokens=2000
    # )
    # refinement_response = response.choices[0].message.content

    print("\n============refinement_response:============\n")
    print(refinement_response)



    # 需要处理refinement_response，将refinement_response中的<START>和<END>标签去掉
    final_prompt = (
        f"{prompt_template}\n\n"
        "以下是一些解题示例:\n"
        f""
    )
    
    return final_prompt


async def main():
    prompt_template = '''
问题：{{query}}
参考信息：{{content}}
用中文回答问题，确保回答清晰、准确，并基于提供的参考信息。

# 输出格式
- 回答应为简洁的中文段落，长度适中，直接回应问题。
- 如果参考信息不足以回答问题，请明确指出并说明原因。
'''
    acc=[0.9, 0.9, 0.85, 0.85, 0.85]
    log_file_path = '/Users/zhangxiaoyu/Desktop/WorkSpace/prompt-language/output/examples/promptor/'
    prompt=await add_few_shot(prompt_template, acc, log_file_path)
    print("\n============prompt:============\n")
    print(prompt)

if __name__ == '__main__':
    import asyncio
    asyncio.run(main())


