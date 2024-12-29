import asyncio
import os
from rich.console import Console
from rich.markdown import Markdown
from prompt_language.utils.model_factory.gemini_model import get_model_response_gemini
from prompt_language.utils.tool_factory.custom.fetch_wechat_url import fetch_wechat_url
from prompt_language.utils.tool_factory.custom.fetch_openai_url import fetch_openai_url

def is_openai_url(url):
    """判断是否是OpenAI的URL"""
    return url.startswith('https://openai.com/') or url.startswith('http://openai.com/')

def read_existing_content(file_path):
    """
    读取已存在的文件内容
    :param file_path: 文件路径
    :return: str 文件内容，如果文件不存在返回None
    """
    try:
        if os.path.exists(file_path):
            print(f"发现已存在的文件: {file_path}")
            with open(file_path, 'r', encoding='utf-8') as f:
                return f.read()
    except Exception as e:
        print(f"读取已存在文件时发生错误: {str(e)}")
    return None

async def fetch_and_summarize(url, name="article", max_retries=3):
    """
    获取文章内容并生成摘要
    :param url: 文章URL
    :param name: 输出文件名（不含扩展名）
    :param max_retries: 最大重试次数
    :return: None
    """
    print(f"\n开始处理文章: {url}")
    
    # 创建output目录
    output_dir = 'output/gemini_conclusion'
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    try:
        # 检查是否存在已经抓取的文件
        original_file = os.path.join(output_dir, f'{name}_original.md')
        text = read_existing_content(original_file)
        
        if text:
            print("使用已存在的文件内容...")
        else:
            print("未找到已存在的文件，开始抓取内容...")
            # 根据URL类型选择不同的抓取方法
            if is_openai_url(url):
                print("检测到OpenAI文章，使用专用抓取方法...")
                text = fetch_openai_url(url, f'gemini_conclusion/{name}_original.md')
            else:
                print("使用通用抓取方法...")
                text = fetch_wechat_url(url, f'gemini_conclusion/{name}_original.md')
        
        if not text:
            print("无法获取文章内容")
            return

        print("\n开始生成文章摘要...")
        # 构建prompt
        prompt = """
        请总结以下学术文章的重点内容，提取出所有关键信息和重要观点，并按要点分条列出，使用Markdown格式输出，保持客观准确，越长越好，越全面越好。

        # Steps

        1.  阅读文章：仔细阅读提供的文章内容，理解其整体主旨和各个部分的具体内容。
        2.  识别关键信息：识别文章中的核心事实、数据、论点和重要陈述。
        3.  提取重要观点：确定文章中作者表达的主要观点、结论和建议。
        4.  组织要点：将提取的关键信息和重要观点进行分类整理，形成逻辑清晰的要点。
        5.  分条列出：使用Markdown格式，将整理好的要点分条列出，善于使用各级标题。
        6.  客观准确：确保总结内容忠实于原文，避免加入个人理解或偏见。
        7.  详细全面：在保持准确性的前提下，尽可能详细地总结文章内容。

        以下是正规学术文章的具体内容：
        
        {content}
        """.format(content=text)

        # 调用Gemini模型（带重试机制）
        print("正在调用Gemini模型生成摘要...")
        response = None
        retry_count = 0
        
        while response is None and retry_count < max_retries:
            if retry_count > 0:
                print(f"第 {retry_count} 次重试...")
            response = await get_model_response_gemini(contents=prompt)
            retry_count += 1
            if response is None and retry_count < max_retries:
                print("Gemini模型返回为空，等待1秒后重试...")
                await asyncio.sleep(1)
        
        if response is None:
            raise Exception("Gemini模型多次返回空结果，请稍后重试")
        
        # 保存总结内容
        summary_path = os.path.join(output_dir, f'{name}_summary.md')
        print(f"\n保存摘要到: {summary_path}")
        with open(summary_path, 'w', encoding='utf-8') as f:
            # 先写入URL
            f.write(f"# Source URL\n{url}\n\n")
            f.write("# Summary\n")
            # 再写入总结内容
            f.write(response)
        
        # 终端显示
        print("\n摘要内容如下:")
        print("="*50)
        console = Console()
        md = Markdown(response)
        console.print(md)
        print("="*50)
        print(f"\n处理完成! 结果已保存到: {summary_path}")

    except Exception as e:
        print(f"处理过程中发生错误: {str(e)}")
        if "Gemini模型多次返回空结果" in str(e):
            print("建议：")
            print("1. 检查网络连接")
            print("2. 确认Gemini API密钥是否正确")
            print("3. 稍后重试")

def main():
    # url = "https://openai.com/index/deliberative-alignment/"
    # name = "deliberative-alignment"

    # url = "https://mp.weixin.qq.com/s/Twljg_p6utB3cxyGuBiWUg"
    # name = "reft"

    url = "https://www.anthropic.com/research/building-effective-agents"
    name = "anthropic-agent-en"

    asyncio.run(fetch_and_summarize(url, name))

if __name__ == "__main__":
    main()

