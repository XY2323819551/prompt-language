from openai import OpenAI
import re

prompt_rules = '''
• 策略一：给出明确的指示                                                                                     
       • 角色扮演: 明确指定 AI 在当前任务中扮演的角色。                                                          
       • 格式规范: 明确规定输出内容的格式、长度和风格。                                                          
       • 示例提供: 提供具体的例子，精确展示期望的结果。                                                          
    • 策略二：提供优质参考资料                                                                                   
       • 明确引用: 指示 AI 参考你提供的资料生成回复。                                                            
       • 引用来源: 要求 AI 在回复中引用参考资料的内容。                                                          
       • 权威性: 优先使用权威的信息来源，减少错误。                                                              
    • 策略三：大任务化小，分步完成                                                                               
       • 分解任务: 明确完整回答请求所需的关键步骤或组成部分。                                                    
       • 逐个提示: 针对每个子任务给出单独的输入提示。                                                            
       • 结果串联: 将前一步的输出用作后一步的输入。                                                              
    • 策略四：让模型 "展示工作"，迭代优化                                                                        
       • 逐步解释: 要求模型在给出最终答案前，逐步解释推理过程。                                                  
       • 自我检查: 提示模型检查自己的工作，找出可能遗漏的要点。
'''


client = OpenAI(
    api_key="sk-9efddec830e34a1d915ebb4af09d26fb",
    base_url="https://api.deepseek.com"
)


async def prompt_optimizer(prompt_template="", ans=""):
    """根据提示词优化建议，优化原始的prompt"""

    prompt = f"""你的任务是根据【提示词撰写总则】和【提示词优化建议】，优化【原始的prompt】。
    
    提示词撰写总则：
    {prompt_rules}
    
    提示词优化建议：
    {ans}
    
    原始的prompt：
    {prompt_template}
    
    ## 输出格式
    1、输出优化后的prompt使用<optimized_prompt></optimized_prompt>包裹，例如：<optimized_prompt>优化后的prompxxxt</optimized_prompt>
    2、请用中文回答
    3、先输出你的思考过程，再输出优化后的prompt
    """

    response = client.chat.completions.create(
        model="deepseek-chat",
        messages=[{
            "role": "user", 
            "content": prompt
        }],
        temperature=0.0,
        max_tokens=2000
    )
    content = response.choices[0].message.content
    match = re.search(r'<optimized_prompt>(.*?)</optimized_prompt>', content, re.DOTALL)
    optimized_prompt = match.group(1) if match else content
    
    return optimized_prompt


async def main():
    prompt_template = "找出符合条件的人员，回答尽量精炼。问题：{{query}}\n参考信息：{{content}}\n"
    analysis_collections = '''
### 可扩展的建议总结：

1. **明确回答要求**：在提示词中明确要求回答内容要"完整、准确且精炼"，以引导模型全面回答问题。
2. **强调参考资料**：强调模型需要根据参考信息来回答问题，确保回答的准确性。
3. **增加引导性语句**：在提示词中加入一些引导性语句，帮助模型更好地理解问题并提取关键信息。

### 改进原始prompt的建议：

**改进后的提示词**：
```
请根据以下参考信息，找出符合条件的人员，并确保回答内容完整、准确且精炼。问题：{{query}}
参考信息：{{content}}
```

**改进点**：
- **明确要求**：在提示词中明确要求回答内容要"完整、准确且精炼"，以引导模型全面回答问题。
- **强调参考资料**：强调模型需要根据参考信息来回答问题，确保回答的准确性。
- **增加引导**：可以在提示词中加入一些引导性语句，帮助模型更好地理解问题并提取关键信息。

通过以上改进，模型应该能够更准确地输出符合标准答案的回答。
'''
    optimized_prompt = await prompt_optimizer(prompt_template=prompt_template, ans=analysis_collections)
    print(optimized_prompt)


if __name__ == '__main__':
    import asyncio
    asyncio.run(main())
