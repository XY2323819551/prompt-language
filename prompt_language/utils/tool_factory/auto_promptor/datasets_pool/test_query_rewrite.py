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
    if res_len > 5 * len_raw or res_len < 0.5 * len_raw:
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
            api_key="sk-9efddec830e34a1d915ebb4af09dxxxx",
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
        evidences.append(prompt)

        response = client.chat.completions.create(
            model="deepseek-chat",
            messages=[{
                "role": "user", 
                "content": prompt
            }],
            temperature=0.0,
            max_tokens=1000
        )
        print("---------------------------------------")
        print(response.choices[0].message.content)
        return response.choices[0].message.content
        
    except Exception as e:
        logging.error(f"调用DeepSeek API时发生错误: {str(e)}")
        return None

DATASET_MAPPING = {
    "rewrite_50v1": "/root/workspace/CognitiveAssistant-AT/query_rewrite/rewrite_50v1.xlsx",
    "context_free_110": "/root/workspace/CognitiveAssistant-AT/query_rewrite/context-free-110-v1.xlsx",
    "query_rewrite_test": "/Users/zhangxiaoyu/Desktop/WorkSpace/prompt-language/prompt_language/utils/tool_factory/auto_promptor/datasets_pool/query_rewrite_test.xlsx"
}

MODEL_NAME = "Tome-M-28"

def benchmark_query_rewrte(prompt_template: str, dataset_name: str = "rewrite_50v1", log_file_path: str = "output/benchmark_result.xlsx"):
    file_path = DATASET_MAPPING.get(dataset_name)
    if not file_path:
        raise ValueError(f"Dataset {dataset_name} not found in mapping")

    origin_query_list, history_message_list, rewritten_query_list, pronouns = read_excel_columns(file_path)
    assert len(origin_query_list) == len(history_message_list) == len(rewritten_query_list) == len(pronouns), "datasets error."
    
    log_llm_answers = []
    log_scores = []
    evidences = []
    for idx in range(len(origin_query_list)):
        origin_query = origin_query_list[idx]
        history_message = history_message_list[idx]
        gold_rewritten_query = rewritten_query_list[idx]
        pronoun = pronouns[idx]
        
        
        response = call_deepseek(origin_query, history_message, prompt_template=prompt_template, evidences=evidences)
        origin_response = response
        
        response = post_process(origin_query, response)

        log_llm_answers.append(response)
        score = compute_score(response, gold_rewritten_query, origin_query, pronoun)
        log_scores.append(score)
        print(f"---------------{idx}-----------------")
        print(f"最最原始的答案：{origin_response}\n")
        print(f"原始问题：{origin_query}")
        print(f"改写问题：{response}")
        print(f"期待改写：{gold_rewritten_query}")
        print(f"最终得分：{score}")
        print("\n\n")

    logs_data = {
        "questions": origin_query_list,
        "gold_answers":rewritten_query_list,
        "llm_responses": log_llm_answers,
        "llm_scores": log_scores,
        "evidences": "",
        "history_message":history_message_list
    }

    final_acc = sum(log_scores) / len(origin_query_list)
    final_acc = round(final_acc, 4)
    print(f"final_acc:\n{final_acc}")

    df = pd.DataFrame(logs_data)
    df.to_excel(log_file_path, index=False)
    print(f"Data has been written to {log_file_path}")
    
    return final_acc

if __name__ == '__main__':
    prompt_template = "我是模板，需要传入变量哦！"
    benchmark_query_rewrte(
        prompt_template=prompt_template,
        dataset_name="rewrite_50v1",
        log_file_path="output/benchmark_query_rewrte_result.xlsx"
    )


