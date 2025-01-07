import re
import json
from DolphinLanguageSDK.code_block.basic_code_block import BasicCodeBlock
from DolphinLanguageSDK.utils.llm_client import LLMClient
from dataclasses import dataclass
'''
12.24流式需求    
每当gvp更新时, yield ""
在使用工具或agent作为的工具时，统一用run_stream
如果结果中有"answer"，answer为结果
没有"answer" 全部返回内容为结果
'''
@dataclass
class PromptCall:
    prompt_str: str
    assign_type: str
    output_var: str
    system_prompt: str
    tools: list

class JudgeBlock(BasicCodeBlock):
    def __init__(self, config=None, globalvariablepool=None, debug_infos=None):
        self.config = config
        self.debug_info = debug_infos
        self.global_variable_pool = globalvariablepool
        self.llm_client = LLMClient(self.config, self.global_variable_pool)
        self.prompt_call_info = None
        self.already_append_flag = False

    def parse_prompt_call(self, content: str) -> PromptCall:
        content = content.strip()
        
        # 去除 /judge/ 前缀
        if content.startswith('/judge/'):
            content = content[7:].strip()
            
        # 初始化结果字段
        system_prompt = ""
        tools = []
        
        # 检查是否包含括号部分，并且括号内包含有效参数
        if (content.startswith('(') and ('system_prompt' in content or 'tools' in content) and ')' in content):
            # 提取括号内的参数
            bracket_start = content.find('(')
            bracket_end = content.find(')')
            params_str = content[bracket_start+1:bracket_end]
            content = content[bracket_end+1:].strip()
            
            # 解析system_prompt
            if 'system_prompt=' in params_str:
                system_start = params_str.find('system_prompt="') + 14
                system_end = params_str.find('"', system_start)
                if system_end != -1:  # 确保找到了结束的引号
                    system_prompt = params_str[system_start:system_end]
            
            # 解析tools
            if 'tools=' in params_str:
                tools_start = params_str.find('tools=[') + 7
                tools_end = params_str.find(']', tools_start)
                if tools_end != -1:  # 确保找到了结束的方括号
                    tools_str = params_str[tools_start:tools_end]
                    tools = [t.strip() for t in tools_str.split(',') if t.strip()]
        
        # 解析基本部分
        pattern = re.compile(r'(.*?)\s*(->|>>)\s*(\w+)$', re.DOTALL)
        match = pattern.match(content)
        
        if not match:
            raise ValueError("Invalid prompt format")
            
        prompt_str = match.group(1).strip()
        assign_type = match.group(2)
        output_var = match.group(3)
        
        return PromptCall(prompt_str=prompt_str, 
                         assign_type=assign_type, 
                         output_var=output_var,
                         system_prompt=system_prompt,
                         tools=tools)

    async def judge_tool_call(self, prompt_str: str) -> tuple[str, dict]:
        tool_name = None
        tool_args = {}
        # 获取全局变量池中的所有工具信息
        tools_info = self.global_variable_pool.get_all_tools()
        tools_describe = []
        for tool_name, tool in tools_info.items():
            tool_desc = f"{tool_name}: {tool.description}\n参数：{tool.inputs}\n\n"
            tools_describe.append(tool_desc)
        tools_describe_str = "\n".join(tools_describe)
        judge_tool_prompt = f"""你是一个智能助手，需要判断用户问题是否可以通过工具来回答。

可用工具列表：
[{tools_describe_str}]

用户问题：{prompt_str}

请判断：
1. 分析用户问题的具体需求
2. 检查是否有工具可以满足这个需求
3. 如果有合适的工具：
   - 选择最合适的工具
   - 提取问题中的关键信息作为工具参数
   - 按指定格式返回工具调用信息
4. 如果没有合适的工具：
   - 返回空值表示使用默认的大模型回答

返回格式要求：
1. 如果需要调用工具，返回JSON格式：
{{"tool_name": "工具名称", "tool_args": {{"参数1": "值1", "参数2": "值2"}}}}

2. 如果不需要调用工具，返回JSON格式：
{{}}

注意：
- 只返回JSON格式的结果，不要有任何其他说明文字
- 工具参数必须与工具描述中的参数名称完全匹配
- 只在非常确定工具可以完成任务时才建议使用工具
- 如有疑虑，优先选择返回None让大模型回答
"""
        messages = [{"role": "user", "content": judge_tool_prompt}]
        judge_tool_res = await self.llm_client.mf_chat(messages)
        try:
            judge_tool_res = json.loads(judge_tool_res)
            tool_name = judge_tool_res.get("tool_name")
            tool_args = judge_tool_res.get("tool_args")
        except Exception as e:
            raise Exception(f"(Prompt block)load judge_tool_res failed: {str(e)}")
        return tool_name, tool_args

    
    async def update_gvpool(self, item):
        assign_type = self.prompt_call_info.assign_type
        output_var = self.prompt_call_info.output_var
        
        if assign_type == "->":
            self.global_variable_pool.set_variable(output_var, item)
        elif assign_type == ">>" and not self.already_append_flag:
            self.already_append_flag = True
            self.global_variable_pool.append_variable(output_var, item)
        elif assign_type == ">>" and self.already_append_flag:
            output_var_value = self.global_variable_pool.get_variable(output_var)  # 拿到output_var对应的value（value是列表）
            output_var_value[-1] = item  # 更新list的最后一项
            self.global_variable_pool.set_variable(output_var, output_var_value)  # 重新set整个变量
    
    
    async def execute(self, content):
        try:
            # step1: 获取替换变量后的content
            variable_index_list = self.global_variable_pool.recognize_variable(content)
            if variable_index_list:
                for variable_name, _ in variable_index_list:
                    variable_value = self.global_variable_pool.get_variable_type(variable_name)
                    content = content.replace(variable_name, str(variable_value))
            
            # step2: 解析prompt_block的3个部分：prompt、赋值方式、赋值变量名
            self.prompt_call_info = self.parse_prompt_call(content)
            prompt_str = self.prompt_call_info.prompt_str

            # step3: 执行prompt；是否调用工具，如果是，则调用工具，否则直接请求llm
            tool_name, tool_args = self.judge_tool_call(prompt_str)
            if tool_name:
                tool_obj = self.global_variable_pool.get_tool(tool_name)
                if not tool_obj:
                    raise Exception(f"Tool not found: {tool_name}")
                tool_obj_info = tool_obj.tool_info()
                if "answer" in tool_obj_info["outputs"]:
                    for resp_item in tool_obj.run_stream(tool_args):
                        await self.update_gvpool(resp_item["answer"])
                        yield resp_item["answer"]
                else:
                    for resp_item in tool_obj.run_stream(tool_args):
                        await self.update_gvpool(resp_item)
                        yield resp_item
                self.already_append_flag = False
            else:
                messages = [{"role": "user", "content": prompt_str}]
                for item in self.llm_client.mf_chat_stream(messages):  # 非流式调用的接口是mf_chat
                    await self.update_gvpool(item)
                    yield item
                self.already_append_flag = False  
        except Exception as e:
            raise Exception(f"Prompt execution failed: {str(e)}")

# 测试代码
if __name__ == "__main__":
    from DolphinLanguageSDK.utils.tools import PoemWriterStreamTest, EmailSenderStreamTest
    from DolphinLanguageSDK.global_variable_pool import GlobalVariablePool
    
    # 初始化变量池
    gvpool = GlobalVariablePool()
    
    # 预设变量
    variables = {
        "email": "test@example.com",
        "message": "这是一封测试邮件",
        "usage": {
            "prompt_tokens": 0,
            "completion_tokens": 0,
            "total_tokens": 0
        }
    }
    gvpool.init_variables(variables)
    
    # 注册工具
    tools = {
        "poem_writer": PoemWriterStreamTest(),
        "email_sender": EmailSenderStreamTest()
    }
    gvpool.init_tools(tools)

    config = {
        'model_name': 'Tome-max',
        'api': 'http://10.4.110.55:9898/api/model-factory/v1/chat/completions',
        'userid': 'b32ad442-aadd-11ef-ac00-3e62f7949701',
        'max_tokens': 2000,
        'temperature': 0
    }
    
    # 初始化 prompt block
    judge_block = JudgeBlock(config=config, globalvariablepool=gvpool)
    
    # 测试用例
    test_cases = [
        # 基本测试
        "查一下上海的天气 ->weather",
        # 带/judge/前缀测试
        "/judge/ 查一下上海的天气 ->weather",
        # 带system_prompt参数测试
        '/judge/(system_prompt="你是一个天气助手")查一下上海的天气 ->weather',
        # 带tools参数测试
        '/judge/(tools=[get_weather])查一下上海的天气 ->weather',
        # 同时带system_prompt和tools参数测试
        '/judge/(system_prompt="你是一个天气助手",tools=[get_weather])查一下上海的天气 ->weather',
        # >>赋值测试
        "查一下上海的天气 >>weather_list",
        # 复杂system_prompt测试
        '/judge/(system_prompt="你是一个专业的天气助手，请用专业的语言描述天气情况",tools=[get_weather,send_email])查一下上海的天气 ->weather',
        # 错误格式测试
        '/judge/system_prompt="xxx"查一下上海的天气 ->weather',  # 缺少括号
        '/judge/(tools=get_weather)查一下上海的天气 ->weather',  # tools格式错误
        '/judge/(system_prompt="缺少引号)查一下上海的天气 ->weather',  # 引号不匹配
        '/judge/(system_prompt="正确",tools=[缺少结束括号)查一下上海的天气 ->weather'  # 方括号不匹配
    ]
    
    # 执行测试
    print("开始测试...")
    for case in test_cases:
        print("\n" + "="*50)
        print("测试输入:", case)
        
        # 解析结果
        parsed = prompt_block.parse_prompt_call(case)
        print("\n解析结果:")
        print(f"提示词: {parsed.prompt_str}")
        print(f"赋值方式: {parsed.assign_type}")
        print(f"输出变量: {parsed.output_var}")
        
        # 工具判断结果
        tool_name, tool_args = prompt_block.judge_tool_call(parsed.prompt_str)
        print("\n工具判断结果:")
        print(f"工具名: {tool_name}")
        print(f"工具参数: {tool_args}")
        
        # 执行结果
        for item in prompt_block.execute(case):
            print("--"*50, end="\n")
            print(item)
            print("\n")

            vars = gvpool.get_all_variables()
            for key, value in vars.items():
                print(f"---key---:{key}\n")
                print(f"---value---:{value}\n")

        result = gvpool.get_variable(parsed.output_var)
        for key, value in vars.items():
            print(f"---key---:{key}\n")
            print(f"---value---:{value}\n")
        print("\n执行结果:", result)
    
    print("\n测试完成!")
