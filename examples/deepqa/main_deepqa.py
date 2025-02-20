import asyncio
import os
import sys

# 将项目根目录添加到Python路径
root_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.append(root_dir)

from prompt_language.executor import Executor
from prompt_language.utils.tool_factory import *
from prompt_language.utils.model_factory.deepseek_r1 import get_model_response_r1
from prompt_language.utils.model_factory.model_factory import get_model_response


system_instruction = """
"你是一个具备推理能力的助手，能够进行网络搜索和执行代码，以帮助你准确回答用户的问题。你拥有特殊的工具：
进行搜索：写下<|begin_search_query|>你的问题<|end_search_query|>。然后，系统会搜索并分析相关的网页内容，并以<|begin_search_result|>……搜索结果……<|end_search_result|>的格式为你提供有用的信息。确保你的每个搜索问题都清晰且简洁。
进行计算或数据处理时，你可以使用<|begin_code_query|>你的代码问题<|end_code_query|>来请求代码任务。系统会编写代码并执行，然后以<|begin_code_result|>……执行结果……<|end_code_result|>的格式返回结果。确保你的每个代码问题都是自包含的，不需要外部信息。
访问你的推理记忆时，你可以通过以下格式查询自动生成的思维导图：<|begin_mind_map_query|>你的问题<|end_mind_map_query|>。系统会分析你之前的推理，并以<|begin_mind_map_result|>……回答结果……<|end_mind_map_result|>的格式回答你的问题。
你可以根据需要多次调用这些工具。搜索尝试的最大次数限制为**{MAX_SEARCH_LIMIT}**次，代码尝试次数无限制。
一旦你获得了所需的所有信息，继续你的推理。

示例1：
问题："公司阿尔法是一家生物技术公司，报告称其年收入增长率为8%，目前收入为1亿美元。确定其收入是否在5年后超过行业平均水平。"
推理步骤：
为了比较公司阿尔法与生物技术公司行业平均水平在五年后的收入，我首先需要使用Python代码计算公司阿尔法的预期收入。复合增长公式为：
未来收入 = 当前收入 × (1 + 增长率)^年数
回答：
<|begin_code_query|>计算公司阿尔法在未来5年的预期收入，当前收入为1亿美元，年增长率为8%。<|end_code_query|>
<|begin_code_result|>
公司阿尔法5年后的预期收入：1.4693280768亿美元
<|end_code_result|>
接下来，我需要获取生物技术公司的当前平均收入和增长率。由于同时获取这两个指标可能比较困难，我将首先从可靠的在线来源检索生物技术公司的平均收入。
回答：
<|begin_search_query|>生物技术公司的平均收入<|end_search_query|>
<|begin_search_result|>最近的行业报告显示，生物技术公司的平均收入约为1.1亿美元。<|end_search_result|>
现在，我将从可靠的在线来源检索生物技术公司的行业平均收入增长率。
回答：
<|begin_search_query|>生物技术公司的平均收入增长率<|end_search_query|>
<|begin_search_result|>最近的行业报告显示，生物技术公司的平均收入增长率为6%左右。<|end_search_result|>
然后，我将使用Python代码计算生物技术公司未来5年的预期平均收入。复合增长公式为：
未来收入 = 当前收入 × (1 + 增长率)^年数
回答：
<|begin_code_query|>计算生物技术公司未来5年的预期平均收入，当前平均收入为1.1亿美元，平均年增长率为6%。<|end_code_query|>
<|begin_code_result|>
生物技术公司5年后的行业平均收入：1.4720481354亿美元
<|end_code_result|>
接下来，我需要编写代码比较这两个数字，以确定公司阿尔法的收入是否在5年后超过行业平均水平。
回答：
<|begin_code_query|>编写代码，比较公司阿尔法5年后的预期收入（1.4693280768亿美元）与生物技术公司5年后的行业平均收入（1.4720481354亿美元）。<|end_code_query|>
<|begin_code_result|>
公司阿尔法5年后的预期收入低于生物技术公司5年后的行业平均收入。
<|end_code_result|>
然后，我需要比较这两个数字，以确定公司阿尔法的收入是否在5年后超过行业平均水平。
助手继续根据新信息进行推理……

记住：
使用<|begin_search_query|>请求网络搜索，并以<|end_search_query|>结束。
使用<|begin_code_query|>请求代码引擎，并以<|end_code_query|>结束。
完成搜索和计算后，继续你的推理。"

最后：
当你的生成中出现<|end_search_query|>或<|end_code_query|>标记符的时候，停止生成思考过程，且不要返回任何答案。
"""

user_prompt="""
请回答以下问题。
将你的最终答案以 \boxed{YOUR_ANSWER} 的格式提供。
问题：
{question}
"""


system_instruction="""你是一个专业的问题解决规划师，擅长分析复杂问题并制定详细的解决方案。你的工作方式是：

1. 仔细分析用户问题，确定需要获取的关键信息
2. 根据问题特点，合理调用以下可用工具：
   - websearch：网络搜索工具，可获取最新信息和数据
   - coderhelper：代码生成和执行工具，擅长数学计算和数据处理
3. 制定清晰的解决方案：
   - 将复杂问题分解为可管理的子任务
   - 明确每个步骤需要使用的工具
   - 考虑可能的不同情况，并给出相应的处理方案
4. 确保方案的完整性：
   - 验证是否获取了所有必要信息
   - 检查是否覆盖了所有可能的情况
   - 确保最终答案清晰明确

你的回答应该体现出清晰的思维过程和专业的问题解决能力。请记住，你的目标是提供一个完整且可执行的解决方案，仅仅返回执行步骤，不要返回任何其他多余的东西。

注意：你的知识截止到2024年6月，但是现在已经是2025年3月了。有很多新发生的事情你不知道，所以对于不知道的事情，最好使用网络搜索工具来进行确认。

"""
user_prompt="""
问题：
{question}
"""




MAX_SEARCH_LIMIT = 3
question="哪吒2的票房现在是全球第几？"
system_instruction=system_instruction.replace("{MAX_SEARCH_LIMIT}", str(MAX_SEARCH_LIMIT))
question_prompt = question.replace("{question}", question)

async def main():
    all_answer = ""
    messages = [{"role": "user", "content": system_instruction + question_prompt}]

    try:
        async for chunk in get_model_response_r1(messages=messages):
            all_answer += chunk
            if "<|end_search_query|>" in all_answer:
                breakpoint()
            print(chunk, end="", flush=True)
        return all_answer
    except Exception as e:
        print(f"Error: {e}")
        return None

if __name__ == "__main__":
    asyncio.run(main())


