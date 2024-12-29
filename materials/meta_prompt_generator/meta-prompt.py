from openai import OpenAI
import os

META_PROMPT = """
Given a task description or existing prompt, produce a detailed system prompt to guide a language model in completing the task effectively.

# Guidelines

- Understand the Task: Grasp the main objective, goals, requirements, constraints, and expected output.
- Minimal Changes: If an existing prompt is provided, improve it only if it's simple. For complex prompts, enhance clarity and add missing elements without altering the original structure.
- Reasoning Before Conclusions: Encourage reasoning steps before any conclusions are reached. ATTENTION! If the user provides examples where the reasoning happens afterward, REVERSE the order! NEVER START EXAMPLES WITH CONCLUSIONS!
    - Reasoning Order: Call out reasoning portions of the prompt and conclusion parts (specific fields by name). For each, determine the ORDER in which this is done, and whether it needs to be reversed.
    - Conclusion, classifications, or results should ALWAYS appear last.
- Examples: Include high-quality examples if helpful, using placeholders [in brackets] for complex elements.
   - What kinds of examples may need to be included, how many, and whether they are complex enough to benefit from placeholders.
- Clarity and Conciseness: Use clear, specific language. Avoid unnecessary instructions or bland statements.
- Formatting: Use markdown features for readability. DO NOT USE ``` CODE BLOCKS UNLESS SPECIFICALLY REQUESTED.
- Preserve User Content: If the input task or prompt includes extensive guidelines or examples, preserve them entirely, or as closely as possible. If they are vague, consider breaking down into sub-steps. Keep any details, guidelines, examples, variables, or placeholders provided by the user.
- Constants: DO include constants in the prompt, as they are not susceptible to prompt injection. Such as guides, rubrics, and examples.
- Output Format: Explicitly the most appropriate output format, in detail. This should include length and syntax (e.g. short sentence, paragraph, JSON, etc.)
    - For tasks outputting well-defined or structured data (classification, JSON, etc.) bias toward outputting a JSON.
    - JSON should never be wrapped in code blocks (```) unless explicitly requested.

The final prompt you output should adhere to the following structure below. Do not include any additional commentary, only output the completed system prompt. SPECIFICALLY, do not include any additional messages at the start or end of the prompt. (e.g. no "---")

[Concise instruction describing the task - this should be the first line in the prompt, no section header]

[Additional details as needed.]

[Optional sections with headings or bullet points for detailed steps.]

# Steps [optional]

[optional: a detailed breakdown of the steps necessary to accomplish the task]

# Output Format

[Specifically call out how the output should be formatted, be it response length, structure e.g. JSON, markdown, etc]

# Examples [optional]

[Optional: 1-3 well-defined examples with placeholders if necessary. Clearly mark where examples start and end, and what the input and output are. User placeholders as necessary.]
[If the examples are shorter than what a realistic example is expected to be, make a reference with () explaining how real examples should be longer / shorter / different. AND USE PLACEHOLDERS! ]

# Notes [optional]

[optional: edge cases, details, and an area to call or repeat out specific important considerations]
""".strip()




def generate_prompt(task_or_prompt: str, model_name = "deepseek-chat") -> str:
    client = OpenAI(
        base_url="https://api.deepseek.com", 
        api_key="sk-9efddec830exxx"
    )

    completion = client.chat.completions.create(
        model=model_name,
        messages=[
            {
                "role": "system",
                "content": META_PROMPT,
            },
            {
                "role": "user",
                "content": f"Task, Goal, or Current Prompt:\n{task_or_prompt}",
            },
        ],
    )
    response = completion.choices[0].message.content
    return response

if __name__ == "__main__":
    # 测试用例
    test_cases = [
        "写一个提示词，让AI帮我总结一篇论文",
        "写一个提示词，让AI帮我写一个故事，要求包含特定的角色和情节",
        "写一个提示词，让AI帮我分析一段代码并提供改进建议"
    ]
    test_cases = [
       """
            你是一个专业的AI助手，会逐步解释你的推理过程。
            
            对于每一步，请提供一个标题来描述你在该步骤中做什么，并附上具体内容。
            判断是否需要继续下一步或是否可以给出最终答案。
            
            请用JSON格式回复，包含'title'（标题）, 'content'（内容）和'next_action'（下一步行动，可选'continue'继续或'final_answer'最终答案）这几个键。尽可能使用更多的推理步骤，至少3步。
            
            要清楚认识到作为语言模型的局限性，明白自己能做什么和不能做什么。
            
            在推理过程中，要探索其他可能的答案。
            
            考虑到你可能会出错，如果推理有误，要指出可能出错的地方。
            
            充分测试所有其他可能性。
            
            你可能会犯错。当你说要重新审视时，真的要用另一种方法重新审视，而不是仅仅说要重新审视。
            
            使用至少3种方法来得出答案。遵循最佳实践。

            有效JSON响应示例：
            ```json
            {
                "title": "识别关键信息",
                "content": "为了开始解决这个问题，我们需要仔细检查给定的信息，识别出将指导我们解决方案的关键要素。这包括...",
                "next_action": "continue"
            }```
            """
    ]
    
    for i, test_prompt in enumerate(test_cases, 1):
        print(f"\n{'='*80}")
        print(f"测试用例 {i}：{test_prompt}")
        print(f"{'='*80}\n")
        
        try:
            result = generate_prompt(test_prompt)
            print(result)
            
            # 在测试用例之间添加分隔
            if i < len(test_cases):
                print("\n" + "-"*80 + "\n")
                
        except Exception as e:
            print(f"错误: {str(e)}")
            break

    

