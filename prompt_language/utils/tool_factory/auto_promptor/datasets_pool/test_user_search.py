import re
import requests
import pandas as pd
import logging
from openai import OpenAI

def csv_to_excel_and_extract_first_column(file_path):
    df = pd.read_excel(file_path)
    questions = df["questions"].tolist()
    gold_answers = df["gold_answers"].tolist()
    gold_scores = df["gold_scores"].tolist()
    llm_contents = df["llm_contents"].tolist()
    return questions, gold_answers, gold_scores, llm_contents

def format_retrieval_response(retrieval_response):
    focus_nodes = []
    contents = []
    
    # 将字符串按照参考信息分割
    info_list = retrieval_response.split('第')[1:]  # 去掉第一个空字符串
    
    for info in info_list:
        # 提取人名
        try:
            doc_name = info.split('个参考信息--《')[1].split('》')[0]
            focus_nodes.append(doc_name)
            
            # 构建内容
            content = f'第{len(focus_nodes)}个参考信息--《{doc_name}》:{info.split("》:")[1]}'
            contents.append(content)
        except Exception as e:
            logging.error(f'解析参考信息出错: {str(e)}')
            continue

    content = ''.join(contents)
    content = content[:int(8000*1.5)]
    return content, focus_nodes

def ado_llm_ad(question, content):
    base = 8000
    while 1:
        payload = {
            "model_name": "Tome-M-28",
            "model_para": {
                "temperature": 0.0,
                "top_p": 0.95,
                "stop": None,
                "frequency_penalty": 0.0,
                "presence_penalty": 0.0,
                "max_new_tokens": 2000,
                "max_tokens": 2000
            },
            "prompt_id": "1857240990809722880",
            "inputs": {
                "query": question,
                "content": content
            }
        }

        llm_model_api = "https://10.4.70.92:8444/api/model-factory/v1/prompt-template-run"
        headers = {'Content-Type': 'application/json', 'appid': 'O28PdxT1DV0aQnmV4dT'}

        print(f"-----len(content)---------: {len(content)}")

        response = requests.post(llm_model_api, headers=headers, json=payload, verify=False)
        if response.status_code != 200:
            base -= 1000
            content = content[:int(base*1.5)]
            print(f"-----base---------: {base}")
            continue

        static_response = ""
        for line in response.iter_lines(decode_unicode=True):
            if line.startswith("data: ") and line != "data: --end--":
                line=line.split("data: ")[-1]
                static_response += line if line != "None" else ""
        return static_response

def get_hit_nodes(llm_response, focus_nodes):
    hit_nodes = []

    if not llm_response:
        return ["抱歉没有答案"]
    elif any(item in llm_response for item in ["抱歉"]):
        return ["抱歉没有答案"]

    for focus_node in focus_nodes:
        if focus_node in llm_response:
            hit_nodes.append(focus_node)
    if hit_nodes:
        return list(set(hit_nodes))
    else:
        return []

def compute_score(hit_nodes, gold_answer, gold_score):
    gold_answer_list = gold_answer.split("**")
    gold_score = int(gold_score)
    assert len(gold_answer_list) == gold_score, f"答案数量{len(gold_answer_list)} 不等于 分数{gold_score}"

    if not hit_nodes:
        return 0
    elif not all(item in gold_answer for item in hit_nodes):
        return 0
    elif "抱歉没有答案" in hit_nodes:
        return -1
    elif set(hit_nodes) == set(gold_answer_list):
        return 1
    elif len(hit_nodes) < len(gold_answer_list):
        return len(hit_nodes) / len(gold_answer_list)
    else:
        return 0

def cur_query_rewrite(query:str) -> str:
    pattern = r'(?:^|[\u4e00-\u9fff])([a-zA-Z]+)'
    query_text = query
    matches = re.findall(pattern, query_text)
    name_map_es = {
        "as":"AnyShare",
        "ab":"AnyBackup",
        "ad":"AnyData",
        "af":"AnyFabric",
        "ar":"AnyRobot"
    }
    for match in matches:
        if match.lower() in ["as","ab","af","ar","ad"]:
            query_text = query_text.replace(match, match + "(" + name_map_es[match.lower()] + ")")
    return query_text

def call_deepseek(query, content, prompt_template="", evidences=[]):
    try:
        client = OpenAI(
            api_key="sk-9efddec830e34a1d915ebb4af09dxxxx",
            base_url="https://api.deepseek.com"
        )
        
        prompt = prompt_template.replace('{{query}}', query).replace('{{content}}', str(content))
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
    "agent_res_0.8414": "/Users/zhangxiaoyu/Desktop/WorkSpace/prompt-language/prompt_language/utils/tool_factory/auto_promptor/datasets_pool/agent_res_0.8414.xlsx",
    "agent_res_test": "/root/workspace/CognitiveAssistant-AT/agent_test/agent_res_test.xlsx",
    "user_search_test": "/Users/zhangxiaoyu/Desktop/WorkSpace/prompt-language/prompt_language/utils/tool_factory/auto_promptor/datasets_pool/user_search_test.xlsx",
    "user_search_test2": "/Users/zhangxiaoyu/Desktop/WorkSpace/prompt-language/prompt_language/utils/tool_factory/auto_promptor/datasets_pool/user_search_test2.xlsx"
}

def benchmark_user_search(prompt_template: str, dataset_name: str = "user_search_test", log_file_path: str = "output/benchmark_result.xlsx"):
    file_path = DATASET_MAPPING.get(dataset_name)
    if not file_path:
        raise ValueError(f"Dataset {dataset_name} not found in mapping")

    
    questions, gold_answers, gold_scores, llm_contents = csv_to_excel_and_extract_first_column(file_path)
    llm_responses = []
    llm_scores = []
    evidences = []
    width = 25

    for idx, question in enumerate(questions):
        gold_answer = gold_answers[idx]
        gold_score = gold_scores[idx]

        question = cur_query_rewrite(question)
        retrieval_response = llm_contents[idx]

        llm_content, focus_nodes = format_retrieval_response(retrieval_response)
        llm_response = call_deepseek(question, llm_content, prompt_template=prompt_template, evidences=evidences)
        llm_responses.append(llm_response)
        hit_nodes = get_hit_nodes(llm_response, focus_nodes)
        llm_score = compute_score(hit_nodes, gold_answer, gold_score)
        llm_scores.append(llm_score)

        print(f"\n----------question: {idx+1}-----------")
        print(f"{'question:':<{width}}{question}")
        print(f"{'gold_answer:':<{width}}{gold_answer}")
        print(f"{'gold_score:':<{width}}{gold_score}")
        print(f"{'llm_response:':<{width}}{llm_response}\n")
        print(f"{'llm_score:':<{width}}{llm_score}\n")

    data = {
        "questions": questions,
        "gold_answers": gold_answers,
        "llm_responses": llm_responses,
        "llm_scores": llm_scores,
        "evidences": evidences,
        "gold_scores": gold_scores,
        "llm_contents": llm_contents
    }

    llm_scores = [0 if score == -1 else score for score in llm_scores]
    final_acc = round(sum(llm_scores)/len(questions), 4)
    print(f"final_acc:{final_acc}\n")

    df = pd.DataFrame(data)
    df.to_excel(log_file_path, index=False)
    print(f"Data has been written to {log_file_path}")
    
    return final_acc

if __name__ == '__main__':
    prompt_template = "我是模板，需要传入变量哦！"
    benchmark_user_search(
        prompt_template=prompt_template,
        dataset_name="agent_res_0.8414",
        log_file_path="output/benchmark_user_search_result.xlsx"
    )
