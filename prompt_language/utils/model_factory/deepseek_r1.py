# -*- coding: utf-8 -*-
import os
import asyncio
from openai import AsyncOpenAI


async def get_client():
    return AsyncOpenAI(
        api_key="sk-65742e37656f4f3b8543e15d44ffa8c2",
        base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",
    )


query = "9.8和9.11谁大"
messages=[{"role": "user", "content": query}]

async def get_model_response_r1(messages):
    is_answering = False   

    client = await get_client()
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


async def main():
    try:
        await get_model_response_r1(messages)
    except Exception as e:
        print(f"发生错误：{e}")


if __name__ == "__main__":
    asyncio.run(main())