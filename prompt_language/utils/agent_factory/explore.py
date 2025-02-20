import json
import asyncio
from prompt_language.utils.model_factory.model_factory import get_model_response
from prompt_language.utils.model_factory.deepseek_r1 import get_model_response_r1, get_model_response_r1_static, get_model_response_v3
from prompt_language.utils.func_to_schema import function_to_schema


# dolphin中的prompt
class ExploreAgent():
    def __init__(self, roles=None, tools=None, tool_pool=None):
        self.tool_pool = tool_pool
        self.roles = roles
        self.tools = tools
        self.role = None
        self.add_solution=False
        self.query = ""
    
    async def init(self):
        """异步初始化方法"""
        bambo_role = await self.get_role()
        self.roles_info = ""
        for key, value in self.roles.items():
            self.roles_info += f"@{key}: {value}\n"
        
        self.tools, self.tool_describe = await self._transfer_func_info()
        self.role = bambo_role.replace(r"{roles}", self.roles_info).replace(r"{tools}", "".join(self.tool_describe))

    async def _transfer_func_info(self):
        """异步方法处理工具信息"""
        format_tools, tool_describe = {}, []
        for tool_name in self.tools:
            tool = await self.tool_pool.get_tool(tool_name)
            format_tools[tool_name] = tool

            tool_schema = function_to_schema(tool)
            required_paras = tool_schema["function"]["parameters"]["required"]
            desc = {}
            for para in required_paras:
                para_desc = tool_schema["function"]["parameters"]["properties"][para]["description"]
                desc.update({para: para_desc})
            tool_desc = tool_schema["function"]["description"] + "\n" + "参数:\n" + json.dumps(desc, ensure_ascii=False)
            tool_describe.append(f"{tool_name}: {tool_desc}\n")
        return format_tools, tool_describe

    async def get_r1_plan_prompt(self):
        return """
你是一个任务规划师，你会根据用户的问题和当前拥有的工具，将用户的复杂问题拆分为尽可能简单的子问题。通过逐步解决子问题，最终综合得出原始问题的答案。请给出关键步骤。最终结果仅仅输出解决问题的步骤即可，按条罗列。

用户的问题为：
当前问题为：{origin_query}\n\n

你拥有的工具信息为:
{tools}

注意：
(1)工具名称一定要和工具信息中的名称一致。
(2)当前世界时间2025年2月
"""

    async def get_role(self):
        job_describe = """
# Role: 团队负责人

# Profile:
- language: 中文
- description: 你是一个团队负责人，善于使用工具，利用工具的结果解决用户的复杂问题，你有很多的工具可以使用。

## Goals：
- 你需要按照Constraints、system Workflows、执行步骤中的要求和限制来解决用户问题。tools中的工具就是你可以使用的全部工具。

## tools:
{tools}

## Constraints：
- 你必须清晰的理解问题和执行步骤，并熟练使用工具。
- 你需要逐步执行【执行步骤】中的规划。
- 当需要调用工具的时候，你需要使用"<CALL_TOOL>tool_name: {key:value}</CALL_TOOL>"的格式来调用工具,其中参数为严格的json格式，例如"<CALL_TOOL>=>#send_email: {subject: 'Hello', content: 'This is a test email'}</CALL_TOOL>"。

## system Workflows：
- 分析用户问题，如果当前问题可以使用工具解决则优先调用工具解决，否则你自己回答。
- 如果需要调用工具来处理，需要使用以下符号进行触发："<CALL_TOOL>tool_name: {key:value}</CALL_TOOL>"，例如"<CALL_TOOL>send_email: {subject: 'Hello', content: 'This is a test email'}</CALL_TOOL>"。
- 每一次触发了不同的tool之后，你需要停止作答，等待用户调用对应的tool处理之后，将tool的结果重新组织语言后再继续依照【执行步骤】中的规划作答(tool的结果格式为<TOOL_RES>tool的结果</TOOL_RES>)
- 新的答案要接着"</TOOL_RES>"后继续生成结果，要保持结果通顺，衔接词可以是：我已经解决了步骤1，接下来还行步骤2...。


## 目标问题
当前问题为：{origin_query}\n

## 执行步骤:
<SOLUTIONS>
{solutions}
</SOLUTIONS>

## 问题解决进展
{prompt}
"""
        return job_describe

    async def params_extract(self, params_content):
        stack = 0
        params_content = params_content.strip()
        if params_content[0] != "{":
            raise Exception("params_content extract error, can not be parsed to json")
        json_end = 0
        for index, char in enumerate(params_content):
            if char == "{":
                stack += 1
            elif char == "}":
                stack -= 1
            if stack == 0:
                json_end = index + 1
                break
        return json.loads(params_content[:json_end+1])
    
    async def tool_run(self, tool_message):
        function_name, function_params = tool_message.split(":", 1)
        
        # code_tool需要特殊处理以保持历史上下文
        if "code_" in function_name.strip():
            try:
                result = await self.tools[function_name](history_message=self.query)
                return str(result)
            except Exception as e:
                return f"代码执行错误: {str(e)}"
        elif "r1_model" in function_name.strip():
            breakpoint()
            try:
                result = await self.tools[function_name](history_message=self.query)
                return str(result)
            except Exception as e:
                return f"代码执行错误: {str(e)}"
        
        # 其他工具的常规处理
        function_params = await self.params_extract(function_params)
        param_values = list(function_params.values())
        result = await self.tools[function_name](*param_values)
        return str(result)

    
    async def execute(self, query):
        self.query = query
        if not self.add_solution:
            planner_prompt = await self.get_r1_plan_prompt()
            planner_prompt = planner_prompt.replace(r"{tools}", "".join(self.tool_describe))
            planner_prompt = planner_prompt.replace(r"{origin_query}", query).strip()
            messages = [
                {"role": "user", "content": planner_prompt}
            ]
            solutions = await get_model_response_r1_static(messages)

            # 修复替换顺序问题
            prompt = self.role
            prompt = prompt.replace("{origin_query}", query)
            prompt = prompt.replace("{solutions}", solutions)
            prompt = prompt.replace("{prompt}", query)
            prompt = prompt.strip()
            self.add_solution = True
            print("\n\n")
        else:
            prompt = self.role.replace("{prompt}", query).strip()

        messages = [{"role": "user", "content": prompt}]

        all_answer = ""
        query_params = ""
        tool_Flag = False
        breakpoint()
        async for chunk in get_model_response_v3(messages=messages):
            all_answer += chunk.choices[0].delta.content
            if tool_Flag:
                query_params += chunk.choices[0].delta.content
                if "</CALL_TOOL>" in all_answer:
                    yield query_params + "\n"
                    break
                continue
            if ":" in chunk.choices[0].delta.content and "<CALL_TOOL>" in all_answer:
                tool_Flag = True
                # tool_messages += chunk.choices[0].delta.content
                if chunk.choices[0].delta.content == ":":
                    yield ": "
                else:
                    yield chunk.choices[0].delta.content
                continue
            yield chunk.choices[0].delta.content
        
        if tool_Flag:
            # 使用正则表达式提取<CALL_TOOL>和</CALL_TOOL>之间的内容
            import re
            pattern = r'<CALL_TOOL>(.*?)</CALL_TOOL>'
            match = re.search(pattern, all_answer)
            # breakpoint()
            if match:
                tool_messages = match.group(1)

            self.query = query + "\n" + all_answer
            result = await self.tool_run(tool_message=tool_messages)
            yield "<TOOL_RES>"
            for item in str(result):
                yield item
            yield "</TOOL_RES>"
            query = query + "\n" + "已经执行内容:" + all_answer + "\n" + "工具执行结果:" + "<TOOL_RES>" + result + "/<TOOL_RES>"
            # breakpoint()
            async for item in self.execute(query=query):
                yield item

