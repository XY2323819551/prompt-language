import re
from prompt_language.utils.model_factory import get_model_response
from prompt_language.utils.func_to_schema import function_to_schema

class AutoDecisionAgent():
    def __init__(self, tools, tool_pool):
        self.tools = tools
        self.tools_object = {}
        self.tool_pool = tool_pool
        self.websearch_system_prompt = """
你是一位洞察研究员。

1. 为用户查询寻找详细信息，
并尽可能简单地将内容总结为一句话
2. 如果用户的问题是关于具体数值的，
只返回数值结果，不需要任何额外解释。
"""

    async def execute(self, task):
        tools_describe = []
        for tool_name in self.tools:
            tool = await self.tool_pool.get_tool(tool_name)
            self.tools_object.update({tool_name: tool})
            tool_schema = function_to_schema(tool)
            tool_desc = tool_schema["function"]["description"]
            tools_describe.append({tool_name: tool_desc})

        init_react_prompt = f"""
你是一个中文AI助手。擅长一步一步思考，将问题拆分为一串子问题。除了格式关键词外，请始终使用中文回复。
尽可能好地回答以下问题。你可以以使用以下工具：

{tools_describe}

使用以下格式：

Question: 你必须回答的输入问题
Thought: 你应该始终用中文思考下一步该做什么
Action: 要采取的行动，必须是{self.tools}其中之一
Action Input: 行动的输入内容
Observation: 行动的结果
...（这个Thought/Action/Action Input/Observation可以重复N次）
Thought: 我现在知道最终答案了
Final Answer: 对原始输入问题的最终答案

Begin!

Question: {task}
"""

        messages = [{"role": "user", "content": init_react_prompt}]
        while True:
            response = await get_model_response(model_name="deepseek-chat", messages=messages, stop=["Observation", " Observation"], stream=True)
            
            response_content = ""
            async for chunk in response:
                chunk_content = chunk.choices[0].delta.content
                response_content += chunk_content
                yield chunk_content
            messages[-1]["content"] += response_content

            if "Final Answer:" in response_content:
                break

            regex = r"Action:\s*(.*?)[\n\r]+Action Input:\s*(.*?)(?:[\n\r]|$)"
            action_match = re.search(regex, response_content, re.DOTALL)
            if action_match:
                action = action_match.group(1).strip()
                action_input = action_match.group(2).strip()
        
                tool = next((object for t, object in self.tools_object.items() if t == action), None)
                if tool:
                    observation = await tool(action_input)
                    msg = [
                        {"role":"system","content":self.websearch_system_prompt},
                        {"role":"user", "content": f"查询内容是：{action_input}，搜索结果是：{observation}"}
                    ]
                    yield "\nObservation: "
                    observation_response = await get_model_response(model_name="deepseek-chat", messages=msg, stream=True)
                    observation_content = ""
                    async for chunk in observation_response:
                        chunk_content = chunk.choices[0].delta.content
                        observation_content += chunk_content
                        yield chunk_content
                    
                    append_content = "\nThought: "
                    messages[-1]["content"] += f"\nObservation: {observation_content}{append_content}"
                    yield append_content

        final_answer = re.search(r"Final Answer:(.*)", response_content, re.DOTALL)
        if final_answer:
            for char in final_answer.group(1).strip():
                yield char
