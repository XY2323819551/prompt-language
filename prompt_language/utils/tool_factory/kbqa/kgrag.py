# -*- coding: utf-8 -*-
import requests
import json
import urllib3
import warnings
import asyncio
from prompt_language.utils.model_factory.deepseek_r1 import get_model_response_r1_static

# 禁用不安全请求警告
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

async def make_api_request(query, history=[]):
    url = "https://116.63.205.204:8444/api/agent-factory/v2/agent/zxy-kgrag-recall"
    headers = {
        "accept": "application/json",
        "appid": "Ns6yi1EhM8lr-7EFiW-",
        "Content-Type": "application/json",
        "Accept-Language": "zh-CN"
    }
    
    payload = {
        "history": history,
        "query": query
    }
    
    try:
        response = requests.post(url, headers=headers, json=payload, verify=False)
        response.raise_for_status()
        response.encoding = 'utf-8'
        
        # 处理SSE格式的响应
        events = response.text.strip().split('event:data')
        if not events:
            return None
            
        # 获取最后一个非空事件
        last_event = None
        for event in events:
            event = event.strip()
            if event.startswith('data:'):
                try:
                    data = json.loads(event[5:].strip())  # 去掉'data:'前缀并解析JSON
                    last_event = data
                except json.JSONDecodeError:
                    continue
                    
        return last_event
                
    except requests.exceptions.RequestException as e:
        print("Error making API request: {}".format(e))
        return None

async def extract_answer(api_response):
    if not api_response:
        return None
    try:
        return api_response.get('answer', {}).get('answer')
    except Exception as e:
        print("Error extracting answer: {}".format(e))
        return None

async def kgrag(query):
    """使用kgrag工具获取问题的参考资料
    Args:
        query (str): 当前问题。
    """
    result = await make_api_request(query)
    
    if result:
        answer = await extract_answer(result)
        if answer:
            prompt = f"""根据参考内容回答用户问题。仔细筛选出满足用户问题中所有条件的答案。注意，参考信息中未明确提及的信息均视为不满足。
                用户问题：
                【{query}】

                所有的参考信息：
                【{answer}】

                用户问题：
                【{query}】
            """
            messages = [{"role":"user", "content":prompt}]
            answer = await get_model_response_r1_static(messages=messages)
            return answer
        else:
            print("无法提取答案")
    else:
        print("API request failed")


async def test():
    query = "agent应用开发组有哪些人"
    await kgrag(query)

if __name__ == "__main__":
    asyncio.run(test())

