from prompt_language.utils.model_factory.deepseek_r1 import get_model_response_v3_static
import asyncio
messages=[]

async def main():
    messages=[{
            "role": "user",
            "content": "角色\n你是一个问题重写专家，可以根据历史对话信息，对当前问题的主语和指代进行补充完善，生成一个语义明确、没有指代的问题。\n\n当前问题为：\n【该组有哪些人】\n\n历史对话信息为：\n【'answer': '对于问题：【张小宇在哪个组】。答案是：张小宇在Agent应用开发组。','think': ''】\n\n# 步骤\n步骤1. 如果历史对话信息和当前问题无关，或无法改写，请忽略后续步骤，直接返回：【重写后的问题】$sub_question。\n步骤2. 如果可以改写，则先识别当前问题中的主语和所有的指代，并显示你的答案。\n步骤3. 从历史对话信息中找出步骤2中涉及的主语或指代的具体内容，要忠于原文，不要少任何一个字。显示你的答案\n步骤4. 结合步骤2和步骤3的结果，将你找到的具体的主语或指代替换到当前问题：【$sub_question】中。重写后的问题尽量简短。显示重写后的问题，输出格式为：【重写后的问题】xxx\n\n# 注意事项\n1. 你只需要补充主语和指代信息即可，不要修改问题本身。\n2. 你有足够的时间，请认真思考后回答。\n"
        }]
    
        
        # 修复：使用 async for 来迭代异步生成器
    response = await get_model_response_v3_static(messages)
    print(response)


if __name__ == "__main__":
    asyncio.run(main())

