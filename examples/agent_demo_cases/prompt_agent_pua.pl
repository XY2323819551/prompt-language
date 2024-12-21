@code(```python
def get_prompt_agent_pua(path):
    with open(path, "r") as f:
        data = f.readlines()
        return "".join(data)
prompt = get_prompt_agent_pua("/Users/zhangxiaoyu/Desktop/WorkSpace/prompt-language/examples/prompt_agent_pua.txt")
```) -> prompt_agent_pua


@agent(
    type="prompt-based", 
    task=$prompt_agent_pua
) -> pua_agent

