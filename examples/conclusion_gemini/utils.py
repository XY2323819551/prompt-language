# -*- coding: utf-8 -*-
import requests
from bs4 import BeautifulSoup
import re
import time
import random

def fetch_wechat_article(url):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    
    try:
        response = requests.get(url, headers=headers)
        response.encoding = 'utf-8'
        
        soup = BeautifulSoup(response.text, 'html.parser')
        
        content = soup.find('div', class_='rich_media_content')
        if content:
            text = content.get_text(strip=True)
            text = re.sub(r'\n+', '\n', text)
            
            with open('pretrain.md', 'w', encoding='utf-8') as f:
                f.write(text)
            return True
    except Exception as e:
        print("Error: %s" % str(e))
        return False

def fetch_openai_article(url):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.9',
        'Accept-Encoding': 'gzip, deflate, br',
        'Connection': 'keep-alive',
        'Cache-Control': 'max-age=0',
        'Sec-Ch-Ua': '"Not_A Brand";v="8", "Chromium";v="120", "Google Chrome";v="120"',
        'Sec-Ch-Ua-Mobile': '?0',
        'Sec-Ch-Ua-Platform': '"macOS"',
        'Upgrade-Insecure-Requests': '1',
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Sec-Fetch-Dest': 'document',
        'Sec-Fetch-Mode': 'navigate',
        'Sec-Fetch-Site': 'none',
        'Sec-Fetch-User': '?1',
        'Pragma': 'no-cache',
        'Priority': 'u=0, i',
        'Cookie': ''  # 如果需要可以添加cookie
    }
    
    try:
        # 添加随机延迟
        time.sleep(random.uniform(1, 3))
        
        session = requests.Session()
        # 先访问主页
        session.get("https://openai.com", headers=headers)
        time.sleep(random.uniform(1, 2))
        
        response = session.get(url, headers=headers)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # 保存原始HTML以便调试
        with open('debug.html', 'w', encoding='utf-8') as f:
            f.write(response.text)
            
        main_content = soup.find('main')
        if not main_content:
            main_content = soup.find('article')
        if not main_content:
            main_content = soup.find('div', {'class': 'content'})
            
        if main_content:
            text = main_content.get_text(strip=True)
            text = re.sub(r'\s+', ' ', text)
            text = re.sub(r'\n+', '\n', text)
            
            with open('openai_article.md', 'w', encoding='utf-8') as f:
                f.write(text)
            return True
        else:
            print("Cannot find main content")
            with open('failed_content.html', 'w', encoding='utf-8') as f:
                f.write(response.text)
            return False
            
    except requests.exceptions.RequestException as e:
        print("Request error: %s" % str(e))
        return False
    except Exception as e:
        print("Other error: %s" % str(e))
        return False

# Test code
if __name__ == "__main__":
    url = "https://openai.com/index/deliberative-alignment/"
    result = fetch_openai_article(url)
    print("Success" if result else "Failed")

