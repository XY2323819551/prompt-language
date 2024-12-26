import groq
import time
import json

# 直接在初始化时传递 api_key
client = groq.Groq(
    api_key="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"
)

def make_api_call(messages, max_tokens, is_final_answer=False, custom_client=None):
    global client
    if custom_client != None:
        client = custom_client
    
    for attempt in range(3):
        try:
            if is_final_answer:
                response = client.chat.completions.create(
                    model="llama-3.1-70b-versatile",
                    messages=messages,
                    max_tokens=max_tokens,
                    temperature=0.2,
            ) 
                return response.choices[0].message.content
            else:
                response = client.chat.completions.create(
                    model="llama-3.1-70b-versatile",
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
    messages = [
        {"role": "system", "content": """You are an expert AI assistant that explains your reasoning step by step. For each step, provide a title that describes what you're doing in that step, along with the content. Decide if you need another step or if you're ready to give the final answer. Respond in JSON format with 'title', 'content', and 'next_action' (either 'continue' or 'final_answer') keys. USE AS MANY REASONING STEPS AS POSSIBLE. AT LEAST 3. BE AWARE OF YOUR LIMITATIONS AS AN LLM AND WHAT YOU CAN AND CANNOT DO. IN YOUR REASONING, INCLUDE EXPLORATION OF ALTERNATIVE ANSWERS. CONSIDER YOU MAY BE WRONG, AND IF YOU ARE WRONG IN YOUR REASONING, WHERE IT WOULD BE. FULLY TEST ALL OTHER POSSIBILITIES. YOU CAN BE WRONG. WHEN YOU SAY YOU ARE RE-EXAMINING, ACTUALLY RE-EXAMINE, AND USE ANOTHER APPROACH TO DO SO. DO NOT JUST SAY YOU ARE RE-EXAMINING. USE AT LEAST 3 METHODS TO DERIVE THE ANSWER. USE BEST PRACTICES.

Example of a valid JSON response:
```json
{
    "title": "Identifying Key Information",
    "content": "To begin solving this problem, we need to carefully examine the given information and identify the crucial elements that will guide our solution process. This involves...",
    "next_action": "continue"
}```
"""},
        {"role": "user", "content": prompt},
        {"role": "assistant", "content": "Thank you! I will now think step by step following my instructions, starting at the beginning after decomposing the problem."}
    ]

    if file_content:
        messages.append({"role": "user", "content": f"Here's some additional context from an uploaded file:\n\n{file_content}\n\nPlease consider this information when answering the query."})
    if image_content:
        messages.append({"role": "user", "content": f"Here's some additional context from an uploaded image:\n\n{image_content}\n\nPlease consider this information when answering the query."})

    
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

        # Yield after each step for Streamlit to update
        yield steps, None  # We're not yielding the total time until the end

    # Generate final answer
    messages.append({"role": "user", "content": "Please provide the final answer based solely on your reasoning above. Do not use JSON formatting. Only provide the text response without any titles or preambles. Retain any formatting as instructed by the original prompt, such as exact formatting for free response or multiple choice."})
    
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
