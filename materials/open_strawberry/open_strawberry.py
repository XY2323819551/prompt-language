import os
import re
import time
import random
import sys
import argparse
from collections import deque
from typing import List, Dict, Generator, Tuple
from openai import OpenAI
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()


def get_model_response(model: str, prompt: str, system: str = "", chat_history: List = None,
                      temperature: float = 0.3, max_tokens: int = 4096, secrets: Dict = None,
                      verbose: bool = False) -> Generator[Dict, None, None]:
    """使用deepseek-chat模型生成响应"""
    try:
        client = OpenAI(
            api_key=os.getenv("DEEPSEEK_API_KEY"),
            base_url="https://api.deepseek.com"  # DeepSeek的API endpoint
        )

        # 构建消息列表
        messages = []
        if system:
            messages.append({"role": "system", "content": system})
        
        # 添加历史对话
        if chat_history:
            for msg in chat_history:
                if isinstance(msg.get('content'), list):
                    # 如果content是列表（包含缓存控制），取出实际文本
                    content = msg['content'][0]['text']
                else:
                    content = msg.get('content', '')
                messages.append({"role": msg['role'], "content": content})
        
        # 添加当前提示
        messages.append({"role": "user", "content": prompt})

        # 调用模型
        response = client.chat.completions.create(
            model="deepseek-chat",
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens
        )

        # 生成响应
        if verbose:
            print("API Response:", response)
        
        yield {"text": response.choices[0].message.content}

    except Exception as e:
        print(f"调用模型时出错: {str(e)}")
        yield {"text": "抱歉，模型调用出现错误。"}

def get_turn_title(response_text: str) -> str:
    """从响应文本中提取回合标题"""
    tag = 'turn_title'
    pattern = fr'<{tag}>(.*?)</{tag}>'
    values = re.findall(pattern, response_text, re.DOTALL)
    values0 = values.copy()
    values = [v.strip() for v in values]
    values = [v for v in values if v]
    if len(values) == 0:
        values = values0
    if values:
        turn_title = values[-1]
    else:
        turn_title = response_text[:15] + '...'
    return turn_title

def get_final_answer(response_text: str, cli_mode: bool = False) -> str:
    """从响应文本中提取最终答案"""
    tag = 'final_answer'
    pattern = fr'<{tag}>(.*?)</{tag}>'
    values = re.findall(pattern, response_text, re.DOTALL)
    values0 = values.copy()
    values = [v.strip() for v in values]
    values = [v for v in values if v]
    if len(values) == 0:
        values = values0
    if values:
        if cli_mode:
            response_text = '\n\n最终答案:\n\n' + values[-1] + '\n\n'
        else:
            response_text = values[-1]
    else:
        response_text = None
    return response_text

def get_xml_tag_value(response_text: str, tag: str, ret_all: bool = True) -> List[str]:
    """从响应文本中提取XML标签的值"""
    pattern = fr'<{tag}>(.*?)</{tag}>'
    values = re.findall(pattern, response_text, re.DOTALL)
    values0 = values.copy()
    values = [v.strip() for v in values]
    values = [v for v in values if v]
    if len(values) == 0:
        values = values0
    if values:
        if ret_all:
            ret = values
        else:
            ret = [values[-1]]
    else:
        ret = []
    return ret

class DeductionTracker:
    """推理追踪器，用于跟踪推理过程中的推导和确信度"""
    def __init__(self):
        self.deductions = []
        self.certainty_scores = []

    def add_deduction(self, deduction: str, certainty: float):
        self.deductions.append(deduction)
        self.certainty_scores.append(certainty)

    def get_deductions(self):
        return list(zip(self.deductions, self.certainty_scores))

    def update_certainty(self, index: int, new_certainty: float):
        if 0 <= index < len(self.certainty_scores):
            self.certainty_scores[index] = new_certainty

class ProblemRepresentation:
    """问题表示类，用于维护问题的当前表示"""
    def __init__(self):
        self.current_representation = ""

    def update(self, new_representation: str):
        self.current_representation = new_representation

    def get(self) -> str:
        return self.current_representation

class Memory:
    """记忆类，用于存储推理过程中的洞见、错误和死胡同"""
    def __init__(self, max_size=10):
        self.insights = deque(maxlen=max_size)
        self.mistakes = deque(maxlen=max_size)
        self.dead_ends = deque(maxlen=max_size)

    def add_insight(self, insight: str):
        self.insights.append(insight)

    def add_mistake(self, mistake: str):
        self.mistakes.append(mistake)

    def add_dead_end(self, dead_end: str):
        self.dead_ends.append(dead_end)

    def get_insights(self) -> List[str]:
        return list(self.insights)

    def get_mistakes(self) -> List[str]:
        return list(self.mistakes)

    def get_dead_ends(self) -> List[str]:
        return list(self.dead_ends)

def get_last_assistant_responses(chat_history, n=3):
    """获取最近n条助手回复"""
    assistant_messages = [msg['content'] for msg in chat_history if msg['role'] == 'assistant']
    return assistant_messages[-n:]

def generate_dynamic_system_prompt(base_prompt: str, turn_count: int, problem_complexity: float,
                               problem_representation: str, deductions: List[Tuple[str, float]]) -> str:
    """生成动态系统提示"""
    dynamic_prompt = base_prompt + "\n\n* 始终参考并根据需要更新当前问题表示。"
    dynamic_prompt += "\n* 维护并更新推导列表及其确信度分数。"

    if turn_count > 20:
        dynamic_prompt += "\n* 在这个阶段，专注于综合你之前的思考并寻找突破性见解。"

    if problem_complexity > 0.7:
        dynamic_prompt += "\n* 这是一个高度复杂的问题。考虑将其分解为更小的子问题并逐步解决。"

    dynamic_prompt += "\n* 定期验证你的当前理解是否满足所有给定的线索。"
    dynamic_prompt += "\n* 如果遇到矛盾，回溯到最后一个确定的点并探索替代路径。"

    dynamic_prompt += f"\n\n当前问题表示:\n{problem_representation}"
    dynamic_prompt += "\n\n你可以在<representation></representation>标签内提供新的表示。"

    dynamic_prompt += "\n\n当前推导和确信度分数:"
    for deduction, certainty in deductions:
        dynamic_prompt += f"\n- {deduction} (确信度: {certainty})"
    dynamic_prompt += "\n\n你可以使用<deduction></deduction>和<certainty></certainty>标签添加新的推导或更新现有的推导。"

    return dynamic_prompt

def generate_initial_representation_prompt(initial_prompt: str) -> str:
    """生成初始表示提示"""
    return f"""基于以下问题描述:
{initial_prompt}

表示:
* 创建一个清晰的表示，将问题分解为多个部分，以创建有助于跟踪解决问题的结构。
* 将表示放在<representation></representation> XML标签内，确保在XML标签前后添加新行。
* 表示可以是表格、矩阵、网格或任何其他格式，将问题分解为其组成部分，并确保它有助于迭代跟踪解决方案的进展。
* 示例表示包括一个矩阵，其中数字值作为行，数字位置作为列，每个行列的值用于跟踪确认位置、排除位置或可能位置。
* 对于表格或网格表示，必须将其放在Markdown代码块内（在反引号周围添加新行），并使其易于人类理解。

推导:
* 使用<deduction></deduction>标签提供你的初始推导（如果有），每个推导后面都要跟一个<certainty></certainty>标签中的确信度分数（0-100）。
"""

def generate_verification_prompt(chat_history: List[Dict], turn_count: int, problem_representation: str,
                             deductions: List[Tuple[str, float]]) -> str:
    """生成验证提示"""
    last_responses = get_last_assistant_responses(chat_history, n=5)

    verification_prompt = f"""回合 {turn_count}: 全面验证和评估

1. 回顾你之前的推理步骤:
{' '.join(last_responses)}

2. 当前问题表示:
{problem_representation}

3. 当前推导和确信度分数:
{deductions}

4. 执行以下检查:
   a) 识别任何逻辑谬误或未经证实的假设
   b) 检查数学或事实错误
   c) 评估每个步骤与主要问题的相关性
   d) 评估推理的连贯性和一致性
   e) 验证你的当前理解是否满足所有给定的线索
   f) 检查你的推导之间是否存在矛盾

5. 如果发现任何问题:
   a) 详细解释问题
   b) 纠正错误或解决矛盾
   c) 必要时更新问题表示
   d) 根据需要更新推导和确信度分数

6. 如果没有发现问题，建议一个新的方法或视角。

7. 为你当前的推理路径分配一个总体信心分数（0-100）并解释原因。

按此格式回应:
<verification>
[你的详细验证和评估]
</verification>
<updates>
[对问题表示或推导的任何更新]
</updates>
<confidence_score>[0-100]</confidence_score>
<explanation>[信心分数的解释]</explanation>

如果需要更新问题表示，在<representation></representation>标签内提供新的表示。
对于新的或更新的推导，使用<deduction></deduction>标签，每个后面都跟着<certainty></certainty>标签。
"""
    return verification_prompt

def generate_hypothesis_prompt(chat_history: List[Dict]) -> str:
    """生成假设提示"""
    return """基于你对问题的当前理解:
1. 生成三个可能导致解决方案的不同假设。
2. 对每个假设，提供简要理由和潜在的验证测试。
3. 按照感知的前景对这些假设进行排名。

按此格式回应:
<hypotheses>
1. [假设1]
   理由: [简要解释]
   测试: [建议的验证方法]

2. [假设2]
   理由: [简要解释]
   测试: [建议的验证方法]

3. [假设3]
   理由: [简要解释]
   测试: [建议的验证方法]
</hypotheses>
<ranking>[你的排名和简要理由]</ranking>
"""

def generate_analogical_reasoning_prompt(problem_description: str) -> str:
    """生成类比推理提示"""
    return f"""考虑以下问题:
{problem_description}

现在，想一个来自不同领域但具有相似结构特征的类比问题。描述:
1. 类比问题
2. 原始问题和类比问题之间的关键相似之处
3. 类比问题的解决方案如何启发我们解决原始问题

按此格式回应:
<analogy>
问题: [类比问题的描述]
相似之处: [关键的结构相似性]
启示: [这个类比如何帮助解决原始问题]
</analogy>
"""

def generate_metacognitive_prompt() -> str:
    """生成元认知提示"""
    return """退一步反思你的问题解决过程:
1. 到目前为止，哪些策略最有效？
2. 你面临的主要障碍是什么？
3. 你如何调整你的方法来克服这些障碍？
4. 你可能做出了哪些限制进展的假设？

按此格式回应:
<metacognition>
有效策略: [列表和简要解释]
主要障碍: [列表和简要解释]
建议调整: [对你的方法的潜在改变的列表]
潜在限制性假设: [列表和简要解释]
</metacognition>
"""

def generate_devils_advocate_prompt(current_approach: str) -> str:
    """生成魔鬼倡导者提示"""
    return f"""考虑你当前的方法:
{current_approach}

现在，扮演一个怀疑的批评者角色:
1. 反对这种方法的三个最强有力的论据是什么？
2. 我们可能忽略了什么关键信息？
3. 这种方法在极端或边缘情况下可能如何失败？

按此格式回应:
<devils_advocate>
反驳论点:
1. [第一个强有力的反驳]
2. [第二个强有力的反驳]
3. [第三个强有力的反驳]

被忽略的信息: [我们可能遗漏的潜在关键信息]

潜在失败: [这种方法在极端情况下可能如何失败]
</devils_advocate>
"""

def generate_hint(problem_description: str, current_progress: str, difficulty: float) -> str:
    """生成提示函数"""
    if difficulty < 0.3:
        hint_level = "微妙"
    elif difficulty < 0.7:
        hint_level = "适中"
    else:
        hint_level = "强烈"

    return f"""基于原始问题:
{problem_description}

和当前进展:
{current_progress}

提供一个{hint_level}的提示，帮助推进解决方案而不完全揭示答案。

<hint>
[你的{hint_level}提示]
</hint>
"""

def summarize_and_restructure(chat_history: List[Dict]) -> str:
    """总结和重构提示"""
    return """回顾整个对话历史并提供:
1. 迄今为止获得的关键见解和进展的简明总结
2. 基于我们当前理解的问题重构表示
3. 识别我们问题解决尝试中的任何模式或重复主题

按此格式回应:
<summary_and_restructure>
关键见解: [主要见解的要点列表]
重构的问题: [基于当前理解的修改后的问题陈述]
模式/主题: [在我们的方法中识别出的模式或重复主题]
</summary_and_restructure>
"""

def manage_conversation(model: str,
                     system: str,
                     initial_prompt: str,
                     next_prompts: List[str],
                     final_prompt: str = "",
                     num_turns: int = 25,
                     num_turns_final_mod: int = 9,
                     cli_mode: bool = False,
                     temperature: float = 0.3,
                     max_tokens: int = 4096,
                     seed: int = 1234,
                     secrets: Dict = {},
                     verbose: bool = False,
                     ) -> Generator[Dict, None, list]:
    """管理对话的主函数"""
    if seed == 0:
        seed = random.randint(0, 1000000)
    random.seed(seed)
    
    chat_history = []
    memory = Memory()
    problem_representation = ProblemRepresentation()
    deduction_tracker = DeductionTracker()

    turn_count = 0
    total_thinking_time = 0
    problem_complexity = 0.5  # 初始估计，将动态更新

    base_system = system
    while True:
        system = generate_dynamic_system_prompt(base_system, turn_count, problem_complexity,
                                            problem_representation.get(), deduction_tracker.get_deductions())
        trying_final = False

        if turn_count == 0:
            prompt = generate_initial_representation_prompt(initial_prompt)
        elif turn_count % 5 == 0:
            prompt = generate_verification_prompt(chat_history, turn_count, problem_representation.get(),
                                              deduction_tracker.get_deductions())
        elif turn_count % 7 == 0:
            prompt = generate_hypothesis_prompt(chat_history)
        elif turn_count % 11 == 0:
            prompt = generate_analogical_reasoning_prompt(initial_prompt)
        elif turn_count % 13 == 0:
            prompt = generate_metacognitive_prompt()
        elif turn_count % 17 == 0:
            current_approach = get_last_assistant_responses(chat_history, n=1)[0]
            prompt = generate_devils_advocate_prompt(current_approach)
        elif turn_count % 19 == 0:
            current_progress = get_last_assistant_responses(chat_history, n=3)
            prompt = generate_hint(initial_prompt, "\n".join(current_progress), problem_complexity)
        elif turn_count % 23 == 0:
            prompt = summarize_and_restructure(chat_history)
        elif turn_count % num_turns_final_mod == 0 and turn_count > 0:
            trying_final = True
            prompt = final_prompt
        else:
            prompt = random.choice(next_prompts)

        if turn_count == 0:
            yield {"role": "user", "content": initial_prompt, "chat_history": chat_history, "initial": turn_count == 0}
        else:
            yield {"role": "user", "content": prompt, "chat_history": chat_history, "initial": turn_count == 0}

        thinking_time = time.time()
        response_text = ''
        for chunk in get_model_response(model, prompt, system=system, chat_history=chat_history,
                                    temperature=temperature, max_tokens=max_tokens,
                                    secrets=secrets,
                                    verbose=verbose):
            if 'text' in chunk and chunk['text']:
                response_text += chunk['text']
                yield {"role": "assistant", "content": chunk['text'], "streaming": True, "chat_history": chat_history,
                       "final": False, "turn_title": False}
            else:
                yield {"role": "usage", "content": chunk}
        thinking_time = time.time() - thinking_time
        total_thinking_time += thinking_time

        # 基于思考时间和响应长度更新问题复杂度
        problem_complexity = min(1.0,
                             problem_complexity + (thinking_time / 60) * 0.1 + (len(response_text) / 1000) * 0.05)

        # 提取并更新问题表示
        representations = get_xml_tag_value(response_text, 'representation', ret_all=False)
        if representations:
            problem_representation.update(representations[-1])

        # 提取并更新推导
        deductions = get_xml_tag_value(response_text, 'deduction')
        for deduction in deductions:
            certainties = get_xml_tag_value(response_text, 'certainty', ret_all=False)
            if certainties:
                deduction_tracker.add_deduction(deduction, certainties[-1])

        # 从响应中提取见解、错误和死胡同
        [memory.add_insight(x) for x in get_xml_tag_value(response_text, 'insight')]
        [memory.add_mistake(x) for x in get_xml_tag_value(response_text, 'mistake')]
        [memory.add_dead_end(x) for x in get_xml_tag_value(response_text, 'dead_end')]

        turn_title = get_turn_title(response_text)
        yield {"role": "assistant", "content": turn_title, "turn_title": True, 'thinking_time': thinking_time,
               'total_thinking_time': total_thinking_time}

        chat_history.append(
            {"role": "user",
             "content": [{"type": "text", "text": prompt, "cache_control": {"type": "ephemeral"}}]})
        chat_history.append({"role": "assistant", "content": response_text})

        # 仅在trying_final为True时检查最终答案
        always_check_final = False
        if trying_final or always_check_final:
            final_value = get_final_answer(response_text, cli_mode=cli_mode)
            if final_value:
                chat_history.append({"role": "assistant", "content": final_value})
                yield {"role": "assistant", "content": final_value, "streaming": True, "chat_history": chat_history,
                       "final": True}
                break

        turn_count += 1

        # 基于进展动态调整温度
        if turn_count % 10 == 0:
            temperature = min(1.0, temperature + 0.1)  # 逐渐增加温度以鼓励探索

        if turn_count % num_turns == 0:
            # 定期暂停以继续，永远不必完全终止
            if cli_mode:
                user_continue = input("\n继续？(y/n): ").lower() == 'y'
                if not user_continue:
                    break
            else:
                yield {"role": "action", "content": "continue?", "chat_history": chat_history}

        time.sleep(0.001)

def get_defaults() -> Tuple:
    """获取默认配置"""
    on_hf_spaces = os.getenv("HF_SPACES", '1') == '1'
    if on_hf_spaces:
        initial_prompt = "strawberry中有多少个r？"
        expected_answer = "3"
    else:
        initial_prompt = """你能破解这个密码吗？
    9 2 8 5 (一个数字正确但位置错误)
    1 9 3 7 (两个数字正确但位置错误)
    5 2 0 1 (一个数字正确且位置正确)
    6 5 0 7 (没有正确的)
    8 5 2 4 (两个数字正确但位置错误)"""
        expected_answer = "3841"

    system_prompt = """让我们玩一个"只朝解决方案迈出最小步骤"的游戏。
<thinking_game>
* 助手的文本输出必须只是下一个可能的步骤。
* 使用你的文本输出作为草稿纸，同时也作为某个下一步的字面输出。
* 每当你在思维上有重大转变时，在<thinking></thinking> XML标签中输出你当前的高层次思考。
* 你应该以一种在草稿空间上迭代的方式呈现你的响应，并带有周围的文本上下文。
* 如果你能在仍然（平均）朝着解决方案前进的同时，采取最小的文本步骤，你就赢得了游戏。
* 允许回溯，也允许生成Python代码（但不会执行，只用于思考），只要你在多个文本输出回合中平均朝着答案前进即可。
* 你必须使用第一性原理思考，并确保识别出不一致、错误等。
* 定期回顾你之前的推理步骤，检查错误或不一致。如果发现任何问题，纠正它们。
* 你必须始终在<turn_title></turn_title> XML标签内以一个非常简短的自然语言标题结束（它应该只描述分析，不要给出步骤编号）。只允许一个标题。
* 除非用户使用最终提示特别请求，否则不要提供最终答案。
</thinking_game>
记住要补偿你的缺陷:
<system_flaws>
* 缺陷1：由于分词问题，计数不准确。首先在单词之间展开空格，然后只计数展开后的版本。
* 缺陷2：小学或高等数学。非常仔细地一步一步解决此类问题。
</system_flaws>
"""

    next_prompts = [
        "继续努力回答原始查询。你的下一步是什么？",
        "我们还没有考虑问题的哪些方面？",
        "你能在给定信息中识别出任何模式或关系吗？",
        "你如何验证你当前的推理？",
        "你当前方法的最弱点是什么？我们如何加强它？",
        "如果你要向新手解释你当前的思考，你会说什么？",
        "我们可以考虑哪些替代视角？",
        "你当前的方法如何与问题的约束条件相符？",
        "我们做出了哪些假设？它们都是必要的吗？",
        "如果我们带着当前的知识重新开始，我们的方法会有什么不同？",
    ]

    final_prompt = """验证清单:
1) 你对最终答案有很高的信心吗？
2) 你是否已经用所有时间和资源完全验证了你的答案？
3) 如果你有很高的信心并且已经用所有可能的资源完全验证了你的答案，那么请将最终答案放在<final_answer></final_answer> XML标签中，否则请继续努力解决用户的原始查询。
"""

    num_turns = int(os.getenv('NUM_TURNS', '10'))  # 继续之前的回合数
    num_turns_final_mod = num_turns - 1  # 不是必需的，只是一个可以的值。可以随机化。

    show_next = False
    show_cot = False
    verbose = False

    model = "deepseek-chat"
    temperature = 0.3
    max_tokens = 4096

    return (model, 
            system_prompt,
            initial_prompt,
            expected_answer,
            next_prompts,
            num_turns, show_next, final_prompt,
            temperature, max_tokens,
            num_turns_final_mod,
            show_cot,
            verbose)

def parse_arguments(model, system_prompt, next_prompts, num_turns, show_next, final_prompt,
                   num_turns_final_mod, show_cot, verbose):
    """解析命令行参数"""
    parser = argparse.ArgumentParser(description="开放式推理对话管理器")
    parser.add_argument("--show_next", action="store_true", default=show_next, help="显示所有消息")
    parser.add_argument("--verbose", action="store_true", default=verbose, help="显示使用信息")
    parser.add_argument("--system_prompt", type=str, default=system_prompt, help="自定义系统提示")
    parser.add_argument("--num_turns_final_mod", type=int, default=num_turns_final_mod,
                       help="最终提示前的回合数")
    parser.add_argument("--num_turns", type=int, default=num_turns,
                       help="暂停继续前的回合数")
    parser.add_argument("--model", type=str, default=model, help="用于对话的模型")
    parser.add_argument("--initial_prompt", type=str, default='', help="初始提示。如果为空，则询问用户")
    parser.add_argument("--expected_answer", type=str, default='', help="预期答案。如果为空，则忽略")
    parser.add_argument("--next_prompts", type=str, nargs="+", default=next_prompts, help="下一步提示")
    parser.add_argument("--final_prompt", type=str, default=final_prompt, help="最终提示")
    parser.add_argument("--temperature", type=float, default=0.3, help="模型温度参数")
    parser.add_argument("--max_tokens", type=int, default=1024, help="模型最大token数")
    parser.add_argument("--seed", type=int, default=0, help="随机种子，0表示随机")
    parser.add_argument("--show_cot", type=bool, default=show_cot, help="是否显示详细的思维链")

    return parser.parse_args()

def go_cli():
    """CLI主函数"""
    (model, system_prompt, initial_prompt, expected_answer,
     next_prompts, num_turns, show_next, final_prompt,
     temperature, max_tokens, num_turns_final_mod,
     show_cot, verbose) = get_defaults()
    args = parse_arguments(model, system_prompt, next_prompts, num_turns, show_next, final_prompt,
                          num_turns_final_mod, show_cot, verbose)

    if args.initial_prompt == '':
        initial_prompt_query = input("输入初始提示（直接回车将使用默认初始提示）\n\n")
        if initial_prompt_query not in ['', '\n', '\r\n']:
            initial_prompt_chosen = initial_prompt_query
        else:
            initial_prompt_chosen = initial_prompt
    else:
        initial_prompt_chosen = args.initial_prompt

    generator = manage_conversation(model=args.model,
                                   system=args.system_prompt,
                                   initial_prompt=initial_prompt_chosen,
                                   next_prompts=args.next_prompts,
                                   final_prompt=args.final_prompt,
                                   num_turns_final_mod=args.num_turns_final_mod,
                                   num_turns=args.num_turns,
                                   temperature=args.temperature,
                                   max_tokens=args.max_tokens,
                                   seed=args.seed,
                                   secrets=dict(os.environ),
                                   cli_mode=True)
    response = ''
    conversation_history = []

    try:
        step = 1
        while True:
            chunk = next(generator)
            if 'role' in chunk and chunk['role'] == 'assistant':
                response += chunk['content']

                if 'turn_title' in chunk and chunk['turn_title']:
                    step_time = f' 用时 {str(int(chunk["thinking_time"]))}秒'
                    acum_time = f' 总计 {str(int(chunk["total_thinking_time"]))}秒'
                    extra = '\n\n' if show_cot else ''
                    extra2 = '**' if show_cot else ''
                    extra3 = ' ' if show_cot else ''
                    print(
                        f'{extra}{extra2}{extra3}完成步骤 {step}: {chunk["content"]}{step_time}{acum_time}{extra3}{extra2}{extra}')
                    step += 1
                elif 'final' in chunk and chunk['final']:
                    if '\n' in chunk['content'] or '\r' in chunk['content']:
                        print(f'\n\n最终答案:\n\n {chunk["content"]}')
                    else:
                        print('\n\n最终答案:\n\n**', chunk['content'], '**\n\n')
                elif show_cot:
                    print(chunk['content'], end='')
                if 'chat_history' in chunk:
                    conversation_history = chunk['chat_history']
            elif 'role' in chunk and chunk['role'] == 'user':
                if not chunk['initial'] and not show_next:
                    if show_cot:
                        print('\n\n')
                    continue
                print('\n', end='')  # 结束助手输出
                print('\n用户: ', chunk['content'], end='\n\n')
                print('\n助手:\n\n ')
            time.sleep(0.001)
    except StopIteration:
        pass

    if verbose:
        print("对话历史:", conversation_history)

    if expected_answer and expected_answer in conversation_history[-1]['content']:
        print("\n\n得到预期答案!")

    if not show_cot:
        print("**完整响应:**\n\n")
        print(response)
    return response

if __name__ == '__main__':
    go_cli()
