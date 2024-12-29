import re
import asyncio
from typing import Dict, List, Optional
from prompt_language.utils.model_factory.gemini_model import get_model_response_gemini


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


def parse_tasks(tasks_xml: str) -> List[Dict]:
    """解析XML格式的任务为任务字典列表"""
    tasks = []
    current_task = {}
    
    for line in tasks_xml.split('\n'):
        line = line.strip()
        if not line:
            continue
            
        if line.startswith("<task>"):
            current_task = {}
        elif line.startswith("<type>"):
            current_task["type"] = line[6:-7].strip()
        elif line.startswith("<description>"):
            current_task["description"] = line[12:-13].strip()
        elif line.startswith("</task>"):
            if "description" in current_task:
                if "type" not in current_task:
                    current_task["type"] = "default"
                tasks.append(current_task)
    
    return tasks

class FlexibleOrchestrator:
    """使用工作者LLM分解任务并并行运行"""
    
    def __init__(
        self,
        orchestrator_prompt: str,
        worker_prompt: str,
    ):
        """使用提示模板初始化"""
        self.orchestrator_prompt = orchestrator_prompt
        self.worker_prompt = worker_prompt

    def _format_prompt(self, template: str, **kwargs) -> str:
        """使用变量格式化提示模板"""
        try:
            return template.format(**kwargs)
        except KeyError as e:
            raise ValueError(f"缺少必需的提示变量: {e}")

    async def process(self, task: str, context: Optional[Dict] = None) -> Dict:
        """通过分解任务并并行运行子任务来处理任务"""
        context = context or {}
        # 步骤1: 获取编排者响应
        orchestrator_input = self._format_prompt(
            self.orchestrator_prompt,
            task=task,
            **context
        )
        orchestrator_response = await get_model_response_gemini(contents=orchestrator_input)
        
        # 解析编排者响应
        analysis = extract_xml(orchestrator_response, "analysis")
        tasks_xml = extract_xml(orchestrator_response, "tasks")
        tasks = parse_tasks(tasks_xml)
        
        print("\n=== 编排者输出 ===")
        print(f"\n分析:\n{analysis}")
        print(f"\n任务:\n{tasks}")
        
        # 步骤2: 并行处理每个任务
        worker_tasks = []
        for task_info in tasks:
            worker_input = self._format_prompt(
                self.worker_prompt,
                original_task=task,
                task_type=task_info['type'],
                task_description=task_info['description'],
                **context
            )
            
            # 创建任务但不立即执行
            worker_tasks.append({
                "type": task_info["type"],
                "description": task_info["description"],
                "prompt": worker_input  # 存储prompt而不是直接创建future
            })
        
        # 并行执行所有任务
        futures = [
            get_model_response_gemini(contents=task_info["prompt"])
            for task_info in worker_tasks
        ]
        responses = await asyncio.gather(*futures)  # 等待所有任务完成
        
        # 处理结果
        worker_results = []
        for task_info, response in zip(worker_tasks, responses):
            result = extract_xml(response, "response")
            
            worker_result = {
                "type": task_info["type"],
                "description": task_info["description"],
                "result": result
            }
            worker_results.append(worker_result)
            
            print(f"\n=== 工作者结果 ({task_info['type']}) ===\n{result}\n")
        
        return {
            "analysis": analysis,
            "worker_results": worker_results,
        }

# 示例用例: 营销文案变体生成
ORCHESTRATOR_PROMPT = """
分析此任务并将其分解为2-3种不同的方法:

任务: {task}

请按以下格式返回响应:

<analysis>
解释你对任务的理解以及哪些变体会有价值。
重点说明每种方法如何服务于任务的不同方面。
</analysis>

<tasks>
    <task>
    <type>正式</type>
    <description>编写一个强调规格的技术版本</description>
    </task>
    <task>
    <type>对话</type>
    <description>编写一个与读者建立联系的友好版本</description>
    </task>
</tasks>
"""

WORKER_PROMPT = """
基于以下内容生成内容:
任务: {original_task}
风格: {task_type}
指南: {task_description}

请按以下格式返回响应:

<response>
在此处放置你的内容,保持指定的风格并完全满足要求。
</response>
"""

async def main():
    orchestrator = FlexibleOrchestrator(
        orchestrator_prompt=ORCHESTRATOR_PROMPT,
        worker_prompt=WORKER_PROMPT,
    )

    results = await orchestrator.process(
        task="为一款新的环保水瓶编写产品描述",
        context={
            "target_audience": "环保意识强的千禧一代",
            "key_features": ["无塑料", "保温", "终身保修"]
        }
    )
    print("\n最终结果:")
    print(results)

if __name__ == "__main__":
    asyncio.run(main()) 

