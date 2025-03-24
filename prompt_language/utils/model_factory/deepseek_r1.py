# -*- coding: utf-8 -*-
import os
import asyncio
from openai import AsyncOpenAI
from openai import OpenAI
import time

async def get_client():
    return AsyncOpenAI(
        api_key="sk-65742e37656f4f3b8543e15d44ffa8c2",
        base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",
    )


query = "9.8和9.11谁大"
messages=[{"role": "user", "content": query}]


# aliyun
async def get_model_response_r1(messages):
    is_answering = False   

    client = await get_client()
    time.sleep(30)
    stream = await client.chat.completions.create(
        model="deepseek-r1",  
        messages=messages,
        stream=True
    )

    print("\n" + "=" * 20 + "思考过程" + "=" * 20 + "\n")

    async for chunk in stream:
        delta = chunk.choices[0].delta

        if not hasattr(delta, 'reasoning_content'):
            continue
        if not getattr(delta, 'reasoning_content', None) and not getattr(delta, 'content', None):
            continue

        if not getattr(delta, 'reasoning_content', None) and not is_answering:
            # print("\n" + "=" * 20 + "完整回复" + "=" * 20 + "\n")
            yield "\n" + "=" * 20 + "完整回复" + "=" * 20 + "\n"
            is_answering = True

        if getattr(delta, 'reasoning_content', None):
            # print(delta.reasoning_content, end='', flush=True)
            yield delta.reasoning_content
        
        elif getattr(delta, 'content', None):
            # print(delta.content, end='', flush=True)
            yield delta.content

# aliyun
async def get_model_response_r1_static(messages):
    is_answering = False   

    client = await get_client()
    # time.sleep(30)
    stream = await client.chat.completions.create(
        model="deepseek-r1",  
        messages=messages,
        stream=True
    )

    print("\n" + "=" * 20 + "思考过程" + "=" * 20 + "\n")
    content, reasoning_content = "", ""
    async for chunk in stream:
        delta = chunk.choices[0].delta

        if not hasattr(delta, 'reasoning_content'):
            continue
        if not getattr(delta, 'reasoning_content', None) and not getattr(delta, 'content', None):
            continue

        if not getattr(delta, 'reasoning_content', None) and not is_answering:
            print("\n" + "=" * 20 + "完整回复" + "=" * 20 + "\n")
            is_answering = True

        if getattr(delta, 'reasoning_content', None):
            print(delta.reasoning_content, end='', flush=True)
            reasoning_content += delta.reasoning_content
            
        elif getattr(delta, 'content', None):
            print(delta.content, end='', flush=True)
            content += delta.content
    return content

# aliyun
# async def get_model_response_v3_static(messages):
#     is_answering = False   

#     client = await get_client()
#     # time.sleep(30)
#     stream = await client.chat.completions.create(
#         model="deepseek-v3",  
#         messages=messages,
#         stream=True
#     )

#     print("\n" + "=" * 20 + "思考过程" + "=" * 20 + "\n")
#     content, reasoning_content = "", ""
#     async for chunk in stream:
#         delta = chunk.choices[0].delta

#         if not hasattr(delta, 'reasoning_content'):
#             continue
#         if not getattr(delta, 'reasoning_content', None) and not getattr(delta, 'content', None):
#             continue

#         if not getattr(delta, 'reasoning_content', None) and not is_answering:
#             print("\n" + "=" * 20 + "完整回复" + "=" * 20 + "\n")
#             is_answering = True

#         if getattr(delta, 'reasoning_content', None):
#             print(delta.reasoning_content, end='', flush=True)
#             reasoning_content += delta.reasoning_content
            
#         elif getattr(delta, 'content', None):
#             print(delta.content, end='', flush=True)
#             content += delta.content
#     breakpoint()
#     return content



# async def get_model_response_r1_static(self, messages):
#     client = OpenAI(
#         base_url='https://api.siliconflow.cn/v1',
#         api_key="sk-atyahnnvfgxogwfopseezxavxrvjqolunozksdlngdwlnzse"
#     )   
#     answer_dict={"reasoning_content":"","content":""}
#     response = client.chat.completions.create(
#         model="deepseek-ai/DeepSeek-R1-Distill-Qwen-14B",
#         messages=messages,
#         stream=True  # 启用流式输出
#     )

#     for chunk in response:
#         chunk_message = chunk.choices[0].delta.content if chunk.choices[0].delta.content else ""
#         chunk_message_reasoning = chunk.choices[0].delta.reasoning_content if chunk.choices[0].delta.reasoning_content else ""
#         answer_dict["reasoning_content"]+=chunk_message_reasoning
#         answer_dict["content"]+=chunk_message
#         yield answer_dict



# siliconflow
async def get_model_response_v3(messages):
    client = OpenAI(
        base_url='https://api.siliconflow.cn/v1',
        api_key="sk-atyahnnvfgxogwfopseezxavxrvjqolunozksdlngdwlnzse"
    )
    time.sleep(30)
    response = client.chat.completions.create(
        model="deepseek-ai/DeepSeek-V3",  # Qwen/Qwen2.5-7B-Instruct、deepseek-ai/DeepSeek-V3
        messages=messages,
        temperature=0.0,
        stream=True  # 启用流式输出
    )

    for chunk in response:
        # content = chunk.choices[0].delta.content if chunk.choices[0].delta.content else ""
        yield chunk

# # siliconflow
async def get_model_response_v3_static(messages):
    client = OpenAI(
        base_url='https://api.siliconflow.cn/v1',
        api_key="sk-atyahnnvfgxogwfopseezxavxrvjqolunozksdlngdwlnzse"
    )
    response = client.chat.completions.create(
        model="deepseek-ai/DeepSeek-V3",  # Qwen/Qwen2.5-7B-Instruct、deepseek-ai/DeepSeek-V3
        messages=messages,
        temperature=0.0,
        stream=True  # 启用流式输出
    )
    all_content = ""
    for chunk in response:
        content = chunk.choices[0].delta.content if chunk.choices[0].delta.content else ""
        print(content, end="", flush=True)
        all_content += content
    return all_content



async def get_model_response_coder(messages):
    client = OpenAI(
        base_url='https://api.siliconflow.cn/v1',
        api_key="sk-atyahnnvfgxogwfopseezxavxrvjqolunozksdlngdwlnzse"
    )
    response = client.chat.completions.create(
        model="Qwen/Qwen2.5-Coder-7B-Instruct",  # Qwen/Qwen2.5-Coder-32B-Instruct、Qwen/Qwen2.5-Coder-7B-Instruct
        messages=messages,
        temperature=0.0,
        stream=True  # 启用流式输出
    )

    all_content = ""
    for chunk in response:
        content = chunk.choices[0].delta.content if chunk.choices[0].delta.content else ""
        print(content, end='', flush=True)
        all_content += content
    return all_content



async def main():
    try:
        messages=[{
            "role": "user",
            "content": "中国大模型行业2025年将会迎来哪些机遇和挑战？"
        }]
        
        # 修复：使用 async for 来迭代异步生成器
        response = await get_model_response_v3_static(messages)
        print(response)
        # async for item in get_model_response_v3(messages):
        #     print(item, end="", flush=True)
            
    except Exception as e:
        print(f"发生错误：{e}")


if __name__ == "__main__":
    asyncio.run(main())