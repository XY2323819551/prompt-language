@code(```python
def read_file(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        data = file.readlines()
        return "".join(data)
file_content = read_file(r"/Users/zhangxiaoyu/Desktop/WorkSpace/prompt-language/assets/macro-o1.txt")
```) -> file_content

@agent(
    type="bambo", 
    task="请根据以下参考信息回答问题：\n$file_content\n\n问题：以采访对话形式介绍一下这篇文章的内容，至少5论对话。", 
    roles = {"host": "采访记者", "expert": "专家"}
) -> interview


