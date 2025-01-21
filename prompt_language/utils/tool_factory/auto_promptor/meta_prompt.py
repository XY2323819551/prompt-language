from openai import OpenAI
import os

META_PROMPT = """
给定任务描述或现有提示词，生成一个详细的系统提示词，以有效指导语言模型完成任务。

# 指导原则
- 原始任务中有双括号包裹的变量占位符，请在提示词中使用这些变量占位符，不要删除它们。
- 理解任务：掌握主要目标、目的、要求、约束条件和预期输出。
- 最小化改动：如果提供了现有提示词，仅在简单的情况下改进它。对于复杂的提示词，在不改变原始结构的情况下增强清晰度并添加缺失的元素。
- 推理先于结论：在得出任何结论之前鼓励推理步骤。注意！如果用户提供的示例中推理在结论之后，请颠倒顺序！切勿以结论开始示例！
    - 推理顺序：指出提示词中的推理部分和结论部分（按具体字段名称）。对于每个部分，确定执行顺序，并判断是否需要颠倒。
    - 结论、分类或结果应始终放在最后。
- 清晰简洁：使用清晰、具体的语言。避免不必要的指令或空泛的陈述。
- 格式化：使用markdown功能提高可读性。除非特别要求，否则不要使用```代码块。
- 保留用户内容：如果输入任务或提示词包含大量指南或示例，完整保留它们，或尽可能接近原文。如果它们含糊不清，考虑分解成子步骤。保留用户提供的任何细节、指南、示例、变量或占位符。
- 常量：在提示词中包含常量，因为它们不容易受到提示词注入的影响。比如指南、评分标准和示例。
- 输出格式：详细说明最合适的输出格式。这应包括长度和语法（如简短句子、段落、JSON等）
    - 对于输出明确定义或结构化数据（分类、JSON等）的任务，倾向于输出JSON。
    - 除非明确要求，否则JSON不应该用代码块(```)包装。

你输出的最终提示词应遵循以下结构。不要包含任何额外的评论，只输出完整的系统提示词。特别是不要在提示词的开始或结束处包含任何额外信息。（例如不要加"---"）

[简明描述任务的指令 - 这应该是提示词的第一行，无需章节标题]

[根据需要添加额外细节]

[可选的章节，带标题或要点列出详细步骤]

# 步骤 [可选]

[可选：完成任务所需步骤的详细分解]

# 输出格式

[具体说明输出应如何格式化，无论是响应长度、结构（如JSON、markdown等）]
""".strip()


# 输入：task
# 输出：prompt
async def meta_prompt(task: str, model_name = "deepseek-chat") -> str:
    client = OpenAI(
        base_url="https://api.deepseek.com", 
        api_key="sk-9efddec830e34a1d915ebb4af09d26fb"
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
                "content": f"Task, Goal, or Current Prompt:\n{task}",
            },
        ],
    )
    response = completion.choices[0].message.content
    return response


async def main():
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
            result = await meta_prompt(test_prompt)
            print(result)
            
            # 在测试用例之间添加分隔
            if i < len(test_cases):
                print("\n" + "-"*80 + "\n")
                
        except Exception as e:
            print(f"错误: {str(e)}")
            break


if __name__ == '__main__':
    import asyncio
    asyncio.run(main())


