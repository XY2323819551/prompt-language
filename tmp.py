def get_prompt_agent_pua(path):
    with open(path, "r") as f:
        data = f.readlines()
        return data
        return "".join(data)
prompt = get_prompt_agent_pua("/Users/zhangxiaoyu/Desktop/WorkSpace/prompt-language/examples/prompt_agent_pua.txt")
breakpoint()
print(prompt)