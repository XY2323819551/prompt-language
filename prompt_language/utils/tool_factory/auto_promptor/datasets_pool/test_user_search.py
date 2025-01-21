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
            api_key="sk-9efddec830e34a1d915ebb4af09d26fb",
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
        # print("---------------------------------------")
        # print(response.choices[0].message.content)
        return response.choices[0].message.content
        
    except Exception as e:
        logging.error(f"调用DeepSeek API时发生错误: {str(e)}")
        return None


def call_aliyun(query, content, prompt_template="", evidences=[]):
    try:
        client = OpenAI(
            api_key="sk-65742e37656f4f3b8543e15d44ffa8c2",
            base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",
        )
        
        prompt = prompt_template.replace('{{query}}', query).replace('{{content}}', str(content))
        evidences.append(prompt)

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
仅返回总体评分，不要返回其他内容!


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
    "agent_res_0.8414": "/Users/zhangxiaoyu/Desktop/WorkSpace/prompt-language/prompt_language/utils/tool_factory/auto_promptor/datasets_pool/agent_res_0.8414.xlsx",
    "agent_res_test": "/root/workspace/CognitiveAssistant-AT/agent_test/agent_res_test.xlsx",
    "user_search_test": "/Users/zhangxiaoyu/Desktop/WorkSpace/prompt-language/prompt_language/utils/tool_factory/auto_promptor/datasets_pool/user_search_test.xlsx",
    "user_search_test2": "/Users/zhangxiaoyu/Desktop/WorkSpace/prompt-language/prompt_language/utils/tool_factory/auto_promptor/datasets_pool/user_search_test2.xlsx",
    "user_search_test100": "/Users/zhangxiaoyu/Desktop/WorkSpace/prompt-language/prompt_language/utils/tool_factory/auto_promptor/datasets_pool/user_search_61.xlsx"
}


def benchmark_user_search(prompt_template: str, dataset_name: str = "user_search_test", metrics: list[str] = ["acc", "fluency", "consistency"], log_file_path: str = "output/benchmark_result.xlsx"):
    file_path = DATASET_MAPPING.get(dataset_name)
    if not file_path:
        raise ValueError(f"Dataset {dataset_name} not found in mapping")

    
    questions, gold_answers, gold_scores, llm_contents = csv_to_excel_and_extract_first_column(file_path)
    llm_responses = []
    llm_scores = []
    evidences = []
    width = 25


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
        


    for idx, question in enumerate(questions):
        gold_answer = gold_answers[idx]
        gold_score = gold_scores[idx]

        question = cur_query_rewrite(question)
        retrieval_response = llm_contents[idx]

        llm_content, focus_nodes = format_retrieval_response(retrieval_response)
        # llm_response = call_deepseek(question, llm_content, prompt_template=prompt_template, evidences=evidences)
        llm_response = call_aliyun(question, llm_content, prompt_template=prompt_template, evidences=evidences)
        
        llm_responses.append(llm_response)
        hit_nodes = get_hit_nodes(llm_response, focus_nodes)
        llm_score = compute_score(hit_nodes, gold_answer, gold_score)
        llm_scores.append(llm_score)

        if fluency_score_flag:
            fluency_score = fluency_score_func(llm_response)
            try:
                fluency_score = float(fluency_score)
            except:
                fluency_scores.append(0.5)
            fluency_scores.append(fluency_score)
        if consistency_score_flag:
            consistency_score = consistency_score_func(llm_response)
            try:
                consistency_score = float(consistency_score)
                if isinstance(consistency_score, float):
                    consistency_scores.append(consistency_score)
                else:
                    consistency_scores.append(0.85)
            except:
                consistency_scores.append(0.85)



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
        "fluency_scores": fluency_scores,
        "consistency_scores": consistency_scores,
        "evidences": llm_contents,  # evidences
        "gold_scores": gold_scores,
        "llm_contents": llm_contents
    }

    df = pd.DataFrame(data)
    df.to_excel(log_file_path, index=False)
    print(f"Data has been written to {log_file_path}")

    try:
        llm_scores = [0 if score == -1 else score for score in llm_scores]
        final_acc = round(sum(llm_scores)/len(questions), 4)
        print(f"final_acc:{final_acc}\n")

        final_fluency_acc = sum(fluency_scores) / len(questions)
        final_fluency_acc = round(final_fluency_acc, 4)
        print(f"final_fluency_acc:\n{final_fluency_acc}")

        print(f"consistency_scores:{consistency_scores}")
        final_consistency_acc = sum(consistency_scores) / len(questions)
        final_consistency_acc = round(final_consistency_acc, 4)
        print(f"final_consistency_acc:\n{final_consistency_acc}")
    except:
        llm_scores = [0 if score == -1 else score for score in llm_scores]
        final_acc = round(sum(llm_scores)/len(questions), 4)
        print(f"final_acc:{final_acc}\n")

    
    
    return final_acc, final_fluency_acc, final_consistency_acc


if __name__ == '__main__':
    prompt_template = "我是模板，需要传入变量哦！"
    final_acc, final_fluency_acc, final_consistency_acc = benchmark_user_search(
        prompt_template=prompt_template,
        dataset_name="agent_res_0.8414",
        log_file_path="output/benchmark_user_search_result.xlsx"
    )
