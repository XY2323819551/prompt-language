import asyncio
import os
import requests
from bs4 import BeautifulSoup
import re
from rich.console import Console
from rich.markdown import Markdown
from prompt_language.utils.model_factory.gemini_model import get_model_response_gemini


async def fetch_and_summarize(url, name="article"):
    # 创建output目录
    if not os.path.exists('output/gemini_conclusion'):
        os.makedirs('output/gemini_conclusion')
    
    # 获取文章内容
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    
    try:
        response = requests.get(url, headers=headers)
        response.encoding = 'utf-8'
        
        soup = BeautifulSoup(response.text, 'html.parser')
        content = soup.find('div', class_='rich_media_content')
        
        if not content:
            print("无法获取文章内容")
            return
            
        # 提取纯文本
        text = content.get_text(strip=True)
        text = re.sub(r'\n+', '\n', text)
        
        # 保存原始内容
        with open(f'output/{name}_original.md', 'w', encoding='utf-8') as f:
            f.write(text)

        # 构建prompt
        prompt = """
        请总结以下文章的重点内容，提取出所有关键信息和重要观点，并按要点分条列出，使用Markdown格式输出，保持客观准确，越长越好，越全面越好。

        # Steps

        1.  阅读文章：仔细阅读提供的文章内容，理解其整体主旨和各个部分的具体内容。
        2.  识别关键信息：识别文章中的核心事实、数据、论点和重要陈述。
        3.  提取重要观点：确定文章中作者表达的主要观点、结论和建议。
        4.  组织要点：将提取的关键信息和重要观点进行分类整理，形成逻辑清晰的要点。
        5.  分条列出：使用Markdown列表格式，将整理好的要点分条列出，善于使用层级标题。
        6.  客观准确：确保总结内容忠实于原文，避免加入个人理解或偏见。
        7.  详细全面：在保持准确性的前提下，尽可能详细地总结文章内容。

        以下是文章内容：
        
        {content}
        """.format(content=text)

        # 调用Gemini模型
        response = await get_model_response_gemini(contents=prompt)
        
        # 保存总结内容
        with open(f'output/{name}_summary.md', 'w', encoding='utf-8') as f:
            # 先写入URL
            f.write(f"# Source URL\n{url}\n\n")
            f.write("# Summary\n")
            # 再写入总结内容
            f.write(response)
        
        # 终端显示
        console = Console()
        md = Markdown(response)
        console.print(md)

    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    url = "https://openai.com/index/deliberative-alignment/"
    asyncio.run(fetch_and_summarize(url, name="deliberative_alignment"))

