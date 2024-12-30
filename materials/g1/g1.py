
import os
import groq
import time
import json
from openai import OpenAI
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

# client = groq.Groq(
#     api_key="gsk_n3kj3xID49YktwiLxxx"
# )

client = OpenAI(
    base_url="https://api.deepseek.com", 
    api_key=os.getenv("DEEPSEEK_API_KEY")
)


def make_api_call(messages, max_tokens, is_final_answer=False, custom_client=None):
    global client
    if custom_client != None:
        client = custom_client
    
    for attempt in range(3):
        try:
            if is_final_answer:
                response = client.chat.completions.create(
                    model="deepseek-chat",  # deepseek-chat、llama-3.1-70b-versatile
                    messages=messages,
                    max_tokens=max_tokens,
                    temperature=0.2,
            ) 
                return response.choices[0].message.content
            else:
                response = client.chat.completions.create(
                    model="deepseek-chat",
                    messages=messages,
                    max_tokens=max_tokens,
                    temperature=0.2,
                    response_format={"type": "json_object"}
                )
                return json.loads(response.choices[0].message.content)
        except Exception as e:
            if attempt == 2:
                if is_final_answer:
                    return {"title": "Error", "content": f"Failed to generate final answer after 3 attempts. Error: {str(e)}"}
                else:
                    return {"title": "Error", "content": f"Failed to generate step after 3 attempts. Error: {str(e)}", "next_action": "final_answer"}
            time.sleep(1)  # Wait for 1 second before retrying

def generate_response(prompt, custom_client=None, file_content=None, image_content=None):
    # 原始prompt
    # messages = [
    #     {
    #         "role": "system", 
    #         "content": """
    #         你是一个专业的AI助手，会逐步解释你的推理过程。
            
    #         对于每一步，请提供一个标题来描述你在该步骤中做什么，并附上具体内容。
    #         判断是否需要继续下一步或是否可以给出最终答案。
            
    #         请用JSON格式回复，包含'title'（标题）, 'content'（内容）和'next_action'（下一步行动，可选'continue'继续或'final_answer'最终答案）这几个键。尽可能使用更多的推理步骤，至少3步。
            
    #         要清楚认识到作为语言模型的局限性，明白自己能做什么和不能做什么。
            
    #         在推理过程中，要探索其他可能的答案。
            
    #         考虑到你可能会出错，如果推理有误，要指出可能出错的地方。
            
    #         充分测试所有其他可能性。
            
    #         你可能会犯错。当你说要重新审视时，真的要用另一种方法重新审视，而不是仅仅说要重新审视。
            
    #         使用至少3种方法来得出答案。遵循最佳实践。

    #         有效JSON响应示例：
    #         ```json
    #         {
    #             "title": "识别关键信息",
    #             "content": "为了开始解决这个问题，我们需要仔细检查给定的信息，识别出将指导我们解决方案的关键要素。这包括...",
    #             "next_action": "continue"
    #         }```
    #         """
    #     },
    #     {"role": "user", "content": prompt},
    #     {"role": "assistant", "content": "好的！我现在会按照指示，从问题分解开始，一步一步地思考。"}
    # ]

    
    # deepseek优化的prompt
    messages = [
        {
            "role": "system", 
            "content": """
            你是一个专业的AI助手，会逐步解释你的推理过程，并使用多种方法验证答案的准确性。

对于每一步，请提供一个标题来描述你在该步骤中做什么，并附上具体内容。判断是否需要继续下一步或是否可以给出最终答案。

请用JSON格式回复，包含'title'（标题）, 'content'（内容）和'next_action'（下一步行动，可选'continue'继续或'final_answer'最终答案）这几个键。尽可能使用更多的推理步骤，至少3步。

在推理过程中，要探索其他可能的答案，并指出可能出错的地方。充分测试所有其他可能性，并使用至少3种方法来得出答案。遵循最佳实践。

# Output Format

输出应为JSON格式，包含以下键：
- `title`: 描述当前步骤的标题。
- `content`: 当前步骤的具体内容。
- `next_action`: 下一步行动，可选'continue'继续或'final_answer'最终答案。

# Examples

输入: "如何计算一个圆的面积？"

输出:
```json
{
    "title": "识别关键信息",
    "content": "为了计算圆的面积，我们需要知道圆的半径。这是计算面积的基本要素。",
    "next_action": "continue"
}
{
    "title": "应用公式",
    "content": "使用公式 A = πr² 来计算圆的面积，其中 A 是面积，r 是半径。",
    "next_action": "continue"
}
{
    "title": "验证结果",
    "content": "通过使用不同的半径值来验证公式的准确性，确保计算结果正确。",
    "next_action": "final_answer"
}
```

# Notes

- 在推理过程中，务必指出可能出错的地方，并重新审视。
- 使用至少3种方法来验证答案的准确性。
- 遵循最佳实践，确保推理过程的严谨性。
            """
        },
        {"role": "user", "content": prompt},
        {"role": "assistant", "content": "好的！我现在会按照指示，从问题分解开始，一步一步地思考。"}
    ]

    if file_content:
        messages.append({"role": "user", "content": f"这是来自上传文件的额外上下文信息：\n\n{file_content}\n\n请在回答问题时考虑这些信息。"})
    if image_content:
        messages.append({"role": "user", "content": f"这是来自上传图片的额外上下文信息：\n\n{image_content}\n\n请在回答问题时考虑这些信息。"})

    
    steps = []
    step_count = 1
    total_thinking_time = 0
    
    while True:
        start_time = time.time()
        step_data = make_api_call(messages, 300, custom_client=custom_client)
        end_time = time.time()
        thinking_time = end_time - start_time
        total_thinking_time += thinking_time
        
        steps.append((f"Step {step_count}: {step_data['title']}", step_data['content'], thinking_time))
        messages.append({"role": "assistant", "content": json.dumps(step_data)})
        if step_data['next_action'] == 'final_answer' or step_count > 25: # Maximum of 25 steps to prevent infinite thinking time. Can be adjusted.
            break
        
        step_count += 1
        yield steps, None

    # Generate final answer
    messages.append({"role": "user", "content": "请根据上述推理过程提供最终答案。不要使用JSON格式。只提供文本回应，不需要任何标题或前言。保持原始提示中要求的格式，如自由回答或多选题的具体格式要求。"})
    
    start_time = time.time()
    final_data = make_api_call(messages, 1200, is_final_answer=True, custom_client=custom_client)
    end_time = time.time()
    thinking_time = end_time - start_time
    total_thinking_time += thinking_time
    
    steps.append(("Final Answer", final_data, thinking_time))

    yield steps, total_thinking_time

def main():
    # 测试问题列表
    test_cases = [
        "9.9和9.11哪个更大？",
        "单词strawberry中有几个r？",
        "将单词hello倒序输出",  # 我把xxx改成了hello作为示例
        "鸡兔同笼，共25双翅膀，64个耳朵，问鸡和兔各有几只？",
        "爱丽丝有3个兄弟，她还有2个姐妹。爱丽丝的兄弟有多少个姐妹？",  # 添加了具体数字
        "我有一张10元和一张50元的人民币，我到商店买了一包烟，花了15元，请问售货员可能找多少钱给我？",
        "一个农夫带两只鸡过河，一只船只能容纳一个人和两个动物，每只船都有一个船夫。那么农夫带着两只鸡过河所需要的最少渡河次数是多少？",
        "请在错误的等式中添加一对括号：1+2*3+4*5+6*7+8*9=479，以使等式成立。"
    ]

    test_cases = [
        "一个农夫带两只鸡过河，一只船只能容纳一个人和两个动物，每只船都有一个船夫。那么农夫带着两只鸡过河所需要的最少渡河次数是多少？",
        "请在错误的等式中添加一对括号：1+2*3+4*5+6*7+8*9=479，以使等式成立。"
    ]
    

    # 遍历每个测试用例
    for i, test_prompt in enumerate(test_cases, 1):
        print(f"\n{'='*80}")
        print(f"测试用例 {i}：{test_prompt}")
        print(f"{'='*80}")
        
        # 使用生成器获取结果
        for steps, total_time in generate_response(test_prompt):
            # 打印每个步骤
            for step_title, step_content, thinking_time in steps:
                print(f"\n{step_title}")
                print("-" * 50)
                print(step_content)
                print(f"思考时间: {thinking_time:.2f}秒")
            
            # 如果有总时间，说明是最后一次迭代
            if total_time is not None:
                print(f"\n总思考时间: {total_time:.2f}秒")
        
        # 在每个测试用例之间添加一个暂停，避免API调用过于频繁
        if i < len(test_cases):
            print("\n等待5秒后继续下一个测试...")
            time.sleep(5)

if __name__ == "__main__":
    main()
