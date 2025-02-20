from prompt_language.utils.model_factory.deepseek_r1 import get_model_response_coder
import asyncio

async def code_tool(history_message={}):
    """
    自动根据历史对话信息生成目标代码并执行，擅长进行数据分析和数学计算，以及生成代码。

    Args:
        history_message (str): 包含对话历史的字符串，通常包含用户查询和工具调用结果。
    """

    prompt = f"""你是一个代码生成助手。请仔细分析以下历史对话信息，并完成以下任务：

1. 从历史对话中理解用户的计算目标
2. 从历史信息中提取出所有有用的信息
3. 生成一段Python代码来实现这个目标
4. 生成的代码必须使用```python ```包裹
5. 重要：计算结果必须存储在名为python_res的变量中

历史对话信息：
{history_message}

请生成相应的Python代码。不需要打印结果，只需要将最终结果存储在python_res变量中。
"""
    
    try:
        messages = [{"role":"user", "content":prompt}]
        code_response = await get_model_response_coder(messages=messages)
        
        # 提取代码部分
        if "```python" in code_response and "```" in code_response:
            code = code_response.split("```python")[1].split("```")[0].strip()
        else:
            code = code_response.strip()
        
        # 创建本地变量字典来存储执行结果
        local_dict = {}
        
        # 执行代码
        exec(code, globals(), local_dict)
        
        # 获取python_res变量的值作为结果
        if 'python_res' in local_dict:
            return local_dict['python_res']
        else:
            return None
            
    except Exception as e:
        return f"代码执行错误: {str(e)}"

async def test_code_tool():
    history = """好的，我将按照上述步骤来解决这个问题。首先，我会使用serpapi_search工具来搜索2023年纽约市和多伦多的人口数据。

<CALL_TOOL>serpapi_search:  {"query": "2023 New York City population"}</CALL_TOOL>
<TOOL_RES>{'type': 'population_result', 'population': '825.8 万', 'year': '2023 年'}</TOOL_RES>好的，根据搜索结果，2023年纽约市的人口为825.8万。

接下来，我将继续搜索多伦多2023年的人口数据。

<CALL_TOOL>serpapi_search:  {"query": "2023 Toronto population"}</CALL_TOOL>
<TOOL_RES>The metro area population of Toronto in 2024 was 6,431,000, a 0.93% increase from 2023. The metro area population of Toronto in 2023 was 6,372,000, a 0.93% increase from 2022. The metro area population of Toronto in 2022 was 6,313,000, a 0.93% increase from 2021.</TOOL_RES>已经执行内容:根据搜索结果，2023年多伦多的都市区人口为6,372,000。

现在，我们已经获得了2023年纽约市和多伦多的人口数据，接下来计算两者的差值。"""
    
    result = await code_tool(history)
    print(f"计算结果: {result}")

if __name__ == "__main__":
    asyncio.run(test_code_tool())



