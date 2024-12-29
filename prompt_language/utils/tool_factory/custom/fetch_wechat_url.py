# -*- coding: utf-8 -*-
import os
import requests
from bs4 import BeautifulSoup
import re



# 只调试了wechat的内容抓取，其他网站需要根据具体情况进行调整
def fetch_wechat_url(url, output_path):
    """
    通用的网页内容抓取函数
    :param url: 网页URL
    :param output_path: 输出路径（相对于output目录），例如：'gemini/article.md'
    :return: str 返回抓取的文本内容，失败返回None
    """
    print(f"\n开始获取文章: {url}")
    
    # 构建完整的输出路径
    full_output_path = os.path.join('output', output_path)
    output_dir = os.path.dirname(full_output_path)
    
    # 确保输出目录存在
    if not os.path.exists(output_dir):
        print(f"创建输出目录: {output_dir}")
        os.makedirs(output_dir, exist_ok=True)
    
    # 构建调试文件的路径
    debug_dir = os.path.join(output_dir, 'debug')
    if not os.path.exists(debug_dir):
        os.makedirs(debug_dir, exist_ok=True)
    
    debug_html = os.path.join(debug_dir, 'debug.html')
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    
    try:
        print("Step 1: 发送请求...")
        response = requests.get(url, headers=headers)
        response.encoding = 'utf-8'
        
        print("Step 2: 保存原始HTML...")
        with open(debug_html, 'w', encoding='utf-8') as f:
            f.write(response.text)
        
        print("Step 3: 解析页面内容...")
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # 尝试不同的内容选择器
        content = None
        selectors = [
            ('div', {'class_': 'rich_media_content'}),  # 微信文章
            ('main', {}),  # 一般网站主要内容
            ('article', {}),  # 博客文章
            ('div', {'class_': 'content'}),  # 通用内容类
            ('div', {'id': 'content'}),  # 通用内容类
        ]
        
        for tag, attrs in selectors:
            content = soup.find(tag, attrs)
            if content:
                print(f"使用选择器找到内容: {tag}, {attrs}")
                break
        
        if not content:
            print("警告: 无法找到文章内容，将使用body内容")
            content = soup.find('body')
            if not content:
                raise Exception("无法获取任何内容")
        
        print("Step 4: 提取文本内容...")
        text = content.get_text(strip=True)
        text = re.sub(r'\s+', ' ', text)
        text = re.sub(r'\n+', '\n', text)
        
        print(f"Step 5: 保存处理后的内容到 {full_output_path}")
        with open(full_output_path, 'w', encoding='utf-8') as f:
            f.write(text)
        
        print("文章获取成功！")
        return text
            
    except Exception as e:
        print(f"发生错误: {str(e)}")
        return None 