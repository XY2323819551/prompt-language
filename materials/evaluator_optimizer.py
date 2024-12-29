import re
import asyncio
from typing import Dict, List, Tuple
from prompt_language.utils.model_factory.gemini_model import get_model_response_gemini

"""
## Evaluator-Optimizer Workflow
In this workflow, one LLM call generates a response while another provides evaluation and feedback in a loop.

### When to use this workflow
This workflow is particularly effective when we have:

- Clear evaluation criteria
- Value from iterative refinement

The two signs of good fit are:

- LLM responses can be demonstrably improved when feedback is provided
- The LLM can provide meaningful feedback itself
"""

def extract_xml(text: str, tag: str) -> str:
    """
    Extracts the content of the specified XML tag from the given text. Used for parsing structured responses 

    Args:
        text (str): The text containing the XML.
        tag (str): The XML tag to extract content from.

    Returns:
        str: The content of the specified XML tag, or an empty string if the tag is not found.
    """
    match = re.search(f'<{tag}>(.*?)</{tag}>', text, re.DOTALL)
    return match.group(1) if match else ""


async def generate(prompt: str, task: str, context: str = "") -> Tuple[str, str]:
    """基于反馈生成并改进解决方案"""
    full_prompt = f"{prompt}\n{context}\n任务: {task}" if context else f"{prompt}\n任务: {task}"
    response = await get_model_response_gemini(contents=full_prompt)
    thoughts = extract_xml(response, "thoughts")
    result = extract_xml(response, "response")
    
    print("\n=== 生成开始 ===")
    print(f"思考过程:\n{thoughts}\n")
    print(f"生成结果:\n{result}")
    print("=== 生成结束 ===\n")
    
    return thoughts, result

async def evaluate(prompt: str, content: str, task: str) -> Tuple[str, str]:
    """评估解决方案是否满足要求"""
    full_prompt = f"{prompt}\n原始任务: {task}\n待评估内容: {content}"
    response = await get_model_response_gemini(contents=full_prompt)
    evaluation = extract_xml(response, "evaluation")
    feedback = extract_xml(response, "feedback")
    
    print("=== 评估开始 ===")
    print(f"状态: {evaluation}")
    print(f"反馈: {feedback}")
    print("=== 评估结束 ===\n")
    
    return evaluation, feedback

async def loop(task: str, evaluator_prompt: str, generator_prompt: str) -> Tuple[str, List[Dict]]:
    """持续生成和评估直到满足要求"""
    memory = []
    chain_of_thought = []
    
    thoughts, result = await generate(generator_prompt, task)
    memory.append(result)
    chain_of_thought.append({"thoughts": thoughts, "result": result})
    
    while True:
        evaluation, feedback = await evaluate(evaluator_prompt, result, task)
        if evaluation == "PASS":
            return result, chain_of_thought
            
        context = "\n".join([
            "之前的尝试:",
            *[f"- {m}" for m in memory],
            f"\n反馈: {feedback}"
        ])
        
        thoughts, result = await generate(generator_prompt, task, context)
        memory.append(result)
        chain_of_thought.append({"thoughts": thoughts, "result": result})

# 示例用例: 迭代编码循环
evaluator_prompt = """
评估以下代码实现的:
1. 代码正确性
2. 时间复杂度
3. 代码风格和最佳实践

你应该只进行评估而不是尝试解决任务。
只有在满足所有标准且没有进一步改进建议时才输出"PASS"。
请使用以下格式简明地输出你的评估。

<evaluation>PASS, NEEDS_IMPROVEMENT, 或 FAIL</evaluation>
<feedback>
需要改进的内容及原因。
</feedback>
"""

generator_prompt = """
你的目标是根据<用户输入>完成任务。如果有来自你之前生成的反馈，
你应该思考这些反馈来改进你的解决方案。

请使用以下格式简明地输出你的答案：

<thoughts>
[你对任务和反馈的理解，以及你计划如何改进]
</thoughts>

<response>
[你的代码实现]
</response>
"""

task = """
<用户输入>
实现一个栈，具有以下操作:
1. push(x)
2. pop()
3. getMin()
所有操作都应该是O(1)时间复杂度。
</用户输入>
"""

async def main():
    result, chain = await loop(task, evaluator_prompt, generator_prompt)
    print("\n最终结果:")
    print(result)
    print("\n思考链:")
    for step in chain:
        print(f"\n思考: {step['thoughts']}")
        print(f"结果: {step['result']}")

if __name__ == "__main__":
    asyncio.run(main())