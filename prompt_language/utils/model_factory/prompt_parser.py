import re
from dataclasses import dataclass

@dataclass
class PromptCall:
    prompt_str: str
    assign_type: str
    output_var: str
    system_prompt: str
    tools: list

def parse_prompt_call(content: str) -> PromptCall:
    content = content.strip()
    
    # 去除 /judge/ 前缀
    if content.startswith('/judge/'):
        content = content[7:].strip()
        
    # 初始化结果字段
    system_prompt = ""
    tools = []
    
    # 检查是否包含括号部分
    if content.startswith('('):
        try:
            # 找到括号内的内容
            bracket_end = content.find(')')
            if bracket_end == -1:
                raise ValueError("Missing closing bracket")
                
            # 解析括号内的参数
            params_str = content[1:bracket_end]
            
            # 解析system_prompt
            if 'system_prompt' in params_str:
                # 找到system_prompt的开始位置
                start = params_str.find('system_prompt')
                # 跳过可能的空格找到等号
                eq_pos = params_str.find('=', start)
                if eq_pos == -1:
                    raise ValueError("Invalid system_prompt format: missing =")
                # 跳过等号和空格找到第一个引号
                quote_start = params_str.find('"', eq_pos)
                if quote_start == -1:
                    raise ValueError("Invalid system_prompt format: missing opening quote")
                # 从引号后开始找结束引号
                quote_pos = quote_start
                while True:
                    quote_pos = params_str.find('"', quote_pos + 1)
                    if quote_pos == -1:
                        raise ValueError("Missing closing quote for system_prompt")
                    # 如果这个引号前面不是转义字符，那么它就是结束引号
                    if params_str[quote_pos - 1] != '\\':
                        break
                system_prompt = params_str[quote_start+1:quote_pos]
            
            # 解析tools
            if 'tools' in params_str:
                # 找到tools的开始位置
                start = params_str.find('tools')
                # 跳过可能的空格找到等号
                eq_pos = params_str.find('=', start)
                if eq_pos == -1:
                    raise ValueError("Invalid tools format: missing =")
                # 跳过等号和空格找到左方括号
                bracket_start = params_str.find('[', eq_pos)
                if bracket_start == -1:
                    raise ValueError("Invalid tools format: missing [")
                # 找到对应的右方括号
                bracket_pos = bracket_start
                count = 1
                while count > 0:
                    bracket_pos += 1
                    if bracket_pos >= len(params_str):
                        raise ValueError("Missing closing ] for tools")
                    if params_str[bracket_pos] == '[':
                        count += 1
                    elif params_str[bracket_pos] == ']':
                        count -= 1
                tools_str = params_str[bracket_start+1:bracket_pos]
                if tools_str.strip():  # 如果tools不为空
                    tools = [t.strip() for t in tools_str.split(',') if t.strip()]
            
            content = content[bracket_end+1:].strip()
        except Exception as e:
            print(f"Parse error for content: {content}")
            raise ValueError(f"Failed to parse parameters: {str(e)}")
    
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

def print_parse_result(case: str, result: PromptCall):
    print("\n" + "="*50)
    print("测试输入:", case)
    print("\n解析结果:")
    print(f"提示词: {result.prompt_str}")
    print(f"赋值方式: {result.assign_type}")
    print(f"输出变量: {result.output_var}")
    print(f"系统提示词: {result.system_prompt}")
    print(f"工具列表: {result.tools}")

if __name__ == "__main__":
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


    # test_cases = [
    #     # # 基本测试
    #     # "查一下上海的天气 ->weather",
    #     # # 带/judge/前缀测试
    #     # "/judge/ 查一下上海的天气 ->weather",
    #     # 带system_prompt参数测试
    #     '/judge/(system_prompt = "你是一个天气助手")   查一下上海的天气,->weather',
    #     '/judge/(system_prompt="你是一个专业的天气助手，请用专业的语言描述天气情况",tools = [get_weather,send_email]) 查一下上海的天气 ->weather',
    # ]
    
    print("开始测试...")
    for case in test_cases:
        try:
            result = parse_prompt_call(case)
            print_parse_result(case, result)
        except Exception as e:
            print("\n" + "="*50)
            print("测试输入:", case)
            print("解析错误:", str(e))
    
    print("\n测试完成!")
