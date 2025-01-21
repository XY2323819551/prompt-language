import re, json
import logging
import requests
import pandas as pd
import yaml
from openai import OpenAI

def read_excel_columns(file_path):
    df = pd.read_excel(file_path)
    origin_query_list = df['origin_query'].tolist()
    history_message_list = df['history_message'].tolist()
    rewritten_query_list = df['rewritten_query'].tolist()
    pronoun = df['pronoun'].tolist()
    return origin_query_list, history_message_list, rewritten_query_list, pronoun

def ado_make_requests(history, query):
    prompt = f"给定前几轮对话内容和当前的最新问题，判断是否需要使用前几轮对话内容对当前的最新问题进行改写。\n历史对话：{history}\n当前最新问题：{query}\n需要改写的一些场景：\n1、当前问题缺少关键信息的候需要补充内容。\n2、当前问题中有代词时，如：它、他、她、其、该、这个等等。3、其他情况均不需要补充信息。\n如需要使用历史信息对当前最新问题改写直接返回【True】，如果不需要则返回【False】。"
    client_url = "http://10.4.119.109:9000/v1/chat/completions"
    body = {
        "model": "internlm2_5-20b-chat-mix",
        "messages": [
            {
                "role": "user",
                "content": prompt
            }
        ],
        "temperature": 0.0,
        "max_tokens": 1000
    }
    headers = {
            'Content-Type': 'application/json'
        }
    
    response = requests.post(client_url, json=body, headers=headers, verify=False)
    if response.status_code != 200:
        raise Exception(f"get response directly from ad: {response.status_code}, error: {response.text}")
    
    response_data = response.json()
    res_content = response_data['choices'][0]['message']['content']
    print("res_content:", res_content)
    if "False" in res_content:
        return False
    else:
        return True

def post_process(origin_query, rewritten_query):
    rewritten_query = rewritten_query.split("【重写后的问题】")[-1].strip()
    rewritten_query = rewritten_query.split("重写后的问题是：")[-1].strip()
    jaccard_dis = len(set(origin_query).intersection(set(rewritten_query))) / len(rewritten_query)
    res_len = len(rewritten_query)
    len_raw = len(origin_query)
    if res_len > 8 * len_raw or res_len < 0.5 * len_raw:
        rewritten_query = origin_query
    return rewritten_query

def compute_score(response, gold_rewritten_query, origin_query, pronoun):
    response = response.lower()
    pronoun=pronoun.strip().lower()
    gold_rewritten_query = gold_rewritten_query.lower()
    origin_query = origin_query.lower()

    if origin_query == pronoun:  
        if gold_rewritten_query != response:
            return 0
    else:
        if "||" in pronoun:
            prolist = pronoun.strip().split("||")
            for pro in prolist:
                if pro.strip() in response:
                    return 1
        elif "**" in pronoun:
            prolist = pronoun.strip().split("**")
            for pro in prolist:
                if pro.strip() not in response:
                    return 0
        elif pronoun not in response:
            return 0
    return 1 

def ado_llm_ad(question, history_message, prompt_id):
    try:
        history_message_content = ""
        history_message = json.loads(history_message.strip())
        for item in history_message:
            if item['role'] == "user":
                history_message_content += "上轮对话的问题是：" + item['content'] + "\n"
            else:
                history_message_content += "上轮对话的回答是：" + item['content'] + "\n"
        history_message = history_message_content
    except:
        history_message = history_message
        
    payload = {
        "model_name": MODEL_NAME,
        "model_para": {
            "temperature": 0.0,
            "top_p": 0.95,
            "stop": None,
            "frequency_penalty": 0.0,
            "presence_penalty": 0.0,
            "max_tokens": 1000
        },
        "prompt_id": prompt_id,
        "inputs": {
            "query": question,
            "history_message": history_message
        }
    }

    llm_model_api = "https://10.4.70.92:8444/api/model-factory/v1/prompt-template-run"
    headers = {'Content-Type': 'application/json', 'appid': 'O28PdxT1DV0aQnmV4dT'}

    response = requests.post(llm_model_api, headers=headers, json=payload, verify=False)
    if response.status_code != 200:
        logging.error(f"request ad model failed! status code is {response.status}. error: {response.text}")
        return ""

    static_response = ""
    for line in response.iter_lines(decode_unicode=True):
        if line.startswith("data: ") and line.strip() != "data: --end--":
            line = line.split("data: ")[-1]
            static_response += line if line.strip() != "None" else ""
    return static_response

def call_deepseek(query, history_message, prompt_template="", evidences=[]):
    try:
        client = OpenAI(
            api_key="sk-9efddec830e34a1d915ebb4af09d26fb",
            base_url="https://api.deepseek.com"
        )

        try:
            history_message_content = ""
            history_message = json.loads(history_message)
            for item in history_message:
                if item['role'] == "user":
                    history_message_content += "上轮对话的问题是：" + item['content'] + "\n"
                else:
                    history_message_content += "上轮对话的回答是：" + item['content'] + "\n"
            history_message = history_message_content
        except:
            history_message = history_message
        
        prompt = prompt_template.replace('{{query}}', query).replace('{{history_message}}', str(history_message))
        evidences.append(str(history_message))


        response = client.chat.completions.create(
            model="deepseek-chat",
            messages=[{
                "role": "user", 
                "content": prompt
            }],
            temperature=0.0,
            max_tokens=1000
        )
        # print("---------------------------------------")
        # print(response.choices[0].message.content)
        return response.choices[0].message.content
        
    except Exception as e:
        logging.error(f"调用DeepSeek API时发生错误: {str(e)}")
        return None

def call_aliyun(query, history_message, prompt_template="", evidences=[]):
    try:
        client = OpenAI(
            api_key="sk-65742e37656f4f3b8543e15d44ffa8c2",
            base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",
        )

        try:
            history_message_content = ""
            history_message = json.loads(history_message)
            for item in history_message:
                if item['role'] == "user":
                    history_message_content += "上轮对话的问题是：" + item['content'] + "\n"
                else:
                    history_message_content += "上轮对话的回答是：" + item['content'] + "\n"
            history_message = history_message_content
        except:
            history_message = history_message
        
        prompt = prompt_template.replace('{{query}}', query).replace('{{history_message}}', str(history_message))
        evidences.append(str(history_message))


        response = client.chat.completions.create(
            model="qwen2.5-14b-instruct",  # qwen2.5-14b-instruct、qwen2.5-7b-instruct
            messages=[{
                "role": "user", 
                "content": prompt
            }],
            temperature=0.0,
            max_tokens=1000
        )
        # print("---------------------------------------")
        # print(response.choices[0].message.content)
        return response.choices[0].message.content
        
    except Exception as e:
        logging.error(f"调用DeepSeek API时发生错误: {str(e)}")
        return None


def fluency_score_func(response):
    client = OpenAI(
            api_key="sk-9efddec830e34a1d915ebb4af09d26fb",
            base_url="https://api.deepseek.com"
    )
    prompt_template = """
你是一位专业的语言评估专家。现在需要你评估一段文本的语言流畅度。

评估维度：
1. 语法正确性：句子结构是否准确，有无语法错误
2. 连贯性：句子之间的过渡是否自然，逻辑是否连贯
3. 表达清晰度：用词是否准确，表达是否清晰易懂
4. 语言自然度：是否符合自然语言表达习惯，是否有机器翻译痕迹

评分标准：
- 使用0-1的分数区间
- 0表示完全不符合要求
- 1表示完全符合要求
- 可以使用小数点后两位，如0.85

请从以下方面输出评估结果：
1. 各维度评分：
   - 语法正确性：[0-1分]
   - 连贯性：[0-1分]
   - 表达清晰度：[0-1分]
   - 语言自然度：[0-1分]
2. 根据各维度评分，给出总体评分：[0-1分]

# 输出格式
仅返回总体评分，不要返回其他内容！

待评估文本：
{{model_response}}

总体评分是：
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
    # print("\n当前case答案流畅度评分\n")
    # print(response.choices[0].message.content)
    return response.choices[0].message.content


def consistency_score_func(response):
    client = OpenAI(
            api_key="sk-9efddec830e34a1d915ebb4af09d26fb",
            base_url="https://api.deepseek.com"
    )
    prompt_template = """
你是一位专业的逻辑分析专家。请评估以下文本的内容一致性，重点检查是否存在前后矛盾或逻辑冲突。

评估维度：
1. 事实一致性：文中陈述的事实是否前后矛盾
2. 观点一致性：表达的观点和立场是否保持一致
3. 数据一致性：提到的数字、日期等信息是否存在冲突
4. 逻辑连贯性：推理过程是否存在逻辑断裂或矛盾

评分标准：
- 使用0-1的分数区间（保留两位小数）
- 0表示存在严重矛盾
- 1表示完全一致

请按照以下格式输出评估结果：

1. 各维度评分：
   - 事实一致性：[0-1分]
   - 观点一致性：[0-1分]
   - 数据一致性：[0-1分]
   - 逻辑连贯性：[0-1分]
2. 根据各维度评分，给出总体一致性评分：[0-1分]

# 输出格式
仅返回总体评分，不要返回其他内容！


待评估文本：
{{model_response}}

总体评分是：
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
    # print("\n当前case答案一致性评分\n")
    # print(response.choices[0].message.content)
    return response.choices[0].message.content


DATASET_MAPPING = {
    "rewrite_50v1": "/root/workspace/CognitiveAssistant-AT/query_rewrite/rewrite_50v1.xlsx",
    "context_free_110": "/root/workspace/CognitiveAssistant-AT/query_rewrite/context-free-110-v1.xlsx",
    "query_rewrite_test": "/Users/zhangxiaoyu/Desktop/WorkSpace/prompt-language/prompt_language/utils/tool_factory/auto_promptor/datasets_pool/query_rewrite_test.xlsx",
    "query_rewrite_test100": "/Users/zhangxiaoyu/Desktop/WorkSpace/prompt-language/prompt_language/utils/tool_factory/auto_promptor/datasets_pool/query_rewrite_30.xlsx"
}

MODEL_NAME = "Tome-M-28"

def benchmark_query_rewrite(prompt_template: str, dataset_name: str = "rewrite_50v1", metrics: list[str] = ["acc", "fluency", "consistency"], log_file_path: str = "output/benchmark_result.xlsx"):
    file_path = DATASET_MAPPING.get(dataset_name)
    if not file_path:
        raise ValueError(f"Dataset {dataset_name} not found in mapping")

    origin_query_list, history_message_list, rewritten_query_list, pronouns = read_excel_columns(file_path)
    assert len(origin_query_list) == len(history_message_list) == len(rewritten_query_list) == len(pronouns), "datasets error."
    
    log_llm_answers = []
    log_scores = []
    evidences = []

    fluency_score_flag, fluency_scores = False, False
    for metric in metrics:
        if metric == "acc":
            pass
        elif metric == "fluency":
            fluency_score_flag = True
            fluency_scores = []
        elif metric == "consistency":
            consistency_score_flag = True
            consistency_scores = []
        
    for idx in range(len(origin_query_list)):
        origin_query = origin_query_list[idx]
        history_message = history_message_list[idx]
        gold_rewritten_query = rewritten_query_list[idx]
        pronoun = pronouns[idx]
        
        
        response = call_deepseek(origin_query, history_message, prompt_template=prompt_template, evidences=evidences)
        origin_response = response
        
        # response = post_process(origin_query, response)

        log_llm_answers.append(response)
        score = compute_score(response, gold_rewritten_query, origin_query, pronoun)
        log_scores.append(score)


        if fluency_score_flag:
            fluency_score = fluency_score_func(response)
            try:
                fluency_score = float(fluency_score)
            except:
                fluency_scores.append(0.5)
            fluency_scores.append(fluency_score)
        if consistency_score_flag:
            consistency_score = consistency_score_func(response)
            try:
                consistency_score = float(consistency_score)
            except:
                consistency_scores.append(0.5)
            consistency_scores.append(consistency_score)


        print(f"---------------{idx}-----------------")
        print(f"最最原始的答案：{origin_response}\n")
        print(f"原始问题：{origin_query}")
        print(f"改写问题：{response}")
        print(f"期待改写：{gold_rewritten_query}")
        print(f"最终得分：{score}")
        print(f"最终fluency得分：{fluency_score}")
        print(f"最终consistency得分：{consistency_score}")
        print("\n\n")

    logs_data = {
        "questions": origin_query_list,
        "gold_answers":rewritten_query_list,
        "llm_responses": log_llm_answers,
        "llm_scores": log_scores,
        "fluency_scores": fluency_scores,
        "consistency_scores": consistency_scores,
        "evidences": evidences,
        "history_message":history_message_list
    }

    try:
        final_acc = sum(log_scores) / len(origin_query_list)
        final_acc = round(final_acc, 4)
        print(f"final_acc:\n{final_acc}")

        final_fluency_acc = sum(fluency_scores) / len(origin_query_list)
        final_fluency_acc = round(final_fluency_acc, 4)
        print(f"final_fluency_acc:\n{final_fluency_acc}")

        final_consistency_acc = sum(consistency_scores) / len(origin_query_list)
        final_consistency_acc = round(final_consistency_acc, 4)
        print(f"final_consistency_acc:\n{final_consistency_acc}")
    except:
        final_acc = sum(log_scores) / len(origin_query_list)
        final_acc = round(final_acc, 4)
        print(f"final_acc:\n{final_acc}")

    df = pd.DataFrame(logs_data)
    df.to_excel(log_file_path, index=False)
    print(f"Data has been written to {log_file_path}")
    
    return final_acc, final_fluency_acc, final_consistency_acc

if __name__ == '__main__':
    prompt_template = "我是模板，需要传入变量哦！"
    final_acc, final_fluency_acc, final_consistency_acc = benchmark_query_rewrite(
        prompt_template=prompt_template,
        dataset_name="rewrite_50v1",
        log_file_path="output/benchmark_query_rewrte_result.xlsx"
    )


