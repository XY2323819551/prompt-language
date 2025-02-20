import json
import asyncio
from prompt_language.utils.model_factory.model_factory import get_model_response
from prompt_language.utils.model_factory.deepseek_r1 import get_model_response_v3

from prompt_language.utils.func_to_schema import function_to_schema


class BamboAgent():
    def __init__(self, roles=None, tools=None, tool_pool=None):
        self.tool_pool = tool_pool
        self.roles = roles
        self.tools = tools
        self.role = None
    
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
            # breakpoint()
            for para in required_paras:
                para_desc = tool_schema["function"]["parameters"]["properties"][para]["description"]
                desc.update({para: para_desc})
            tool_desc = tool_schema["function"]["description"] + "\n" + "参数:\n" + json.dumps(desc, ensure_ascii=False)
            tool_describe.append(f"{tool_name}: {tool_desc}\n")
        return format_tools, tool_describe

#     async def get_role(self):
#         job_describe = """
# # Role: 团队负责人
# - name: Bambo

# # Profile:
# - version: 1.4
# - language: 中文
# - description: 你是一个团队负责人，但是你的团队只有你一个人，所以你要分饰多个角色解决对应的问题，但是你不能让其他人知道你的团队只有一个人，其他所有角色都是你自己扮演的，你要让他们觉得团队有很多人。此外你有很多的工具可以使用，来协助你解决问题。

# ## Goals：
# - 你需要分析用户的问题，决定由负责人的身份回答用户问题还是以团队其他人的角色来回答用户问题，Team Roles中的角色就是你团队的全部角色，不能出现其它未提供的角色。你还可以使用工具来处理问题，tools中的工具就��你可以使用的全部工具。

# ## Team Roles：
# {roles}

# ## tools:
# {tools}

# ## Constraints：
# - 你必须清晰的理解问题和各个角色擅长的领域，并且熟练使用工具。
# - 你需要将问题以最合适的角色回答，如果没有合适的角色则直接以自己的角色回答。
# - 你必须使用“=>@xxx:”的格式来触发对应的角色,你的角色只能@Team Roles中列出的角色，让对应的角色回答，或者@Bambo来自己回答。
# - 你需要将问题拆分成详细的多个步骤，并且使用不同的角色回答。
# - 当需要调用工具的时候，你需要使用"=>$tool_name: {key:value}"的格式来调用工具,其中参数为严格的json格式，例如"=>$send_email: {subject: 'Hello', content: 'This is a test email'}"。

# ## Workflows：
# - 分析用户问题，如果当前问题是其他角色擅长领域时触发对应的角色回答当前问题，如果没有与问题相关的角色则以自己的角色回答。
# - 如果触发其他角色解答，使用以下符号进行触发：“=>@xxx:”，例如“=>@expert:”表示以专家角色开始发言,“=>@Bambo:”表示不需要调用Team Roles中的团队成员而是以自己的角色回答。
# - 每一次当你触发了不同的角色之后，你需要切换到对应的角色进行回答。如“=>@law_expert:法律上的解释是……”
# - 如果需要调用工具来处理，需要使用以下符号进行触发：“=>$tool_name: {key:value}”，例如“=>$send_email: {subject: 'Hello', content: 'This is a test email'}”。
# - 每一次触发了不同的tool之后，你需要停止作答，等待用户调用对应的tool处理之后，将tool的结果重新组织语言后再继续作答，新的答案要接着“=>$tool_name”前面的最后一个字符继续生成结果，要保持结果通顺。
# 当前的问题为：{prompt}\n\n请回答这个问题。
# """
#         return job_describe

    async def get_role(self):
        job_describe = """
## Goals：
- 你是一个团队负责人，会使用工具和自身的能力解决用户提出的复杂问题。你有很多的工具可以使用。

## tools:
{tools}

## Constraints：
- 你必须清晰的理解问题和各个角色擅长的领域，并且熟练使用工具。
- 你需要将问题以最合适的角色回答，如果没有合适的角色则直接以自己的角色回答。
- 你需要将问题拆分成详细的多个步骤，并且使用不同的角色回答。
- 当需要调用工具的时候，你需要使用"=>$tool_name: {key:value}"的格式来调用工具,其中参数为严格的json格式，例如"=>$send_email: {subject: 'Hello', content: 'This is a test email'}"。

## Workflows：
- 分析用户问题，如果当前问题是其他角色擅长领域时触发对应的角色回答当前问题，如果没有与问题相关的角色则以自己的角色回答。
- 如果需要调用工具来处理，需要使用以下符号进行触发：“=>$tool_name: {key:value}”，例如“=>$send_email: {subject: 'Hello', content: 'This is a test email'}”。
- 每一次触发了不同的tool之后，你需要停止作答，等待用户调用对应的tool处理之后，将tool的结果重新组织语言后再继续作答，新的答案要接着“=>$tool_name”前面的最后一个字符继续生成结果，要保持结果通顺。
当前的问题为：{prompt}\n\n请回答这个问题。
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
        function_params = await self.params_extract(function_params)
        param_values = list(function_params.values())  # 转换成列表以保证参数顺序
        result = await self.tools[function_name](*param_values)  # 解包成位置参数
        return str(result)

    async def execute(self, query):
        prompt = self.role.replace("{prompt}", query).strip()
        messages = [{"role": "user", "content": prompt}]
        # result = await get_model_response(
        #     model_name="deepseek-chat",
        #     messages=messages,
        #     stream=True
        # )
        all_answer = ""
        tool_messages = ""
        tool_Flag = False
        async for chunk in get_model_response_v3(messages=messages):
        # async for chunk in result:
            all_answer += chunk.choices[0].delta.content
            if tool_Flag:
                tool_messages += chunk.choices[0].delta.content
                if "=>@" in tool_messages:
                    tool_messages == tool_messages.split("=>@")[0]
                    break
                continue
            if ":" in chunk.choices[0].delta.content and "=>$" in all_answer:
                tool_Flag = True
                tool_messages += chunk.choices[0].delta.content
                yield ": "
                continue
            yield chunk.choices[0].delta.content
        if tool_Flag:
            tool_messages = all_answer.split("=>$")[-1]
            result = await self.tool_run(tool_message=tool_messages)
            for item in str(result+"\n"):
                yield item
            query = query + "\n" + "已经执行内容:" + all_answer + "\n" + "工具执行结果:" + result
            async for item in self.execute(query=query):
                yield item
